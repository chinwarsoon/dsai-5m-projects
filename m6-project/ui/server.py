"""
M6 RAG Agent Web Server
Serves the HTML interface and provides API endpoints for RAG queries
"""

import sys
import os
import json
import requests
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Add parent directory to path to import engine modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine.logger import Logger
from engine.csv_loader import CSVLoader
from engine.grouping import get_grouping_manager
from engine.embeddings import get_embedding_function
from engine.vector_db import DocumentStore, get_vector_database
from engine.retriever import get_advanced_retriever
from engine.llm_integration import get_ollama_llm, get_rag_pipeline

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Global variables for RAG pipeline components
logger = None
csv_loader = None
grouping_strategy = None
embedding_function = None
vector_db = None
retriever = None
llm = None
rag_pipeline = None

# Configuration
CONFIG_PATH = Path(__file__).parent.parent / 'config' / 'm6_config.json'
DATA_PATH = Path(__file__).parent.parent / 'data' / 'processed_dcc_universal.csv'
VECTOR_DB_PATH = Path(__file__).parent.parent / 'data' / 'chroma_db'


def get_ollama_status():
    """
    Return lightweight Ollama availability status for the configured model.
    """
    if not llm:
        return "not_loaded"

    try:
        response = requests.get(f"{llm.base_url}/api/tags", timeout=2)
        if response.status_code != 200:
            return "unavailable"

        models = response.json().get('models', [])
        model_names = {model.get('name') for model in models}
        return "available" if llm.model_name in model_names else "model_missing"
    except Exception:
        return "unavailable"


def initialize_rag_pipeline():
    """
    Initialize the RAG pipeline components
    """
    global logger, csv_loader, grouping_strategy, embedding_function
    global vector_db, retriever, llm, rag_pipeline
    
    print("=" * 60)
    print("M6 RAG Agent Web Server - Initialization")
    print("=" * 60)
    
    # Load configuration
    print("[1/8] Loading configuration...")
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)
    print("      ✓ Configuration loaded")
    
    # Initialize logger
    print("[2/8] Initializing logger...")
    logger = Logger(config)
    logger.enter_function("initialize_rag_pipeline")
    logger.info("Initializing RAG pipeline", "initialize_rag_pipeline")
    print("      ✓ Logger initialized")
    
    try:
        # Load CSV data
        csv_loader = CSVLoader(config, logger)
        df = csv_loader.load_csv(str(DATA_PATH))
        df = csv_loader.process_by_priority(df)
        logger.info(f"Loaded CSV with {len(df)} rows", "initialize_rag_pipeline")
        
        # Initialize grouping strategy
        grouping_strategy = get_grouping_manager(config, logger)
        
        # Initialize embedding function
        embedding_function = get_embedding_function(config, logger)
        logger.info("Embedding function initialized", "initialize_rag_pipeline")
        
        # Initialize vector database
        vector_db = get_vector_database(config, logger, embedding_function)
        
        # Check if collection exists and has documents
        print("[7/8] Checking vector database collection...")
        collection_count = vector_db.get_collection_count()
        if collection_count == 0:
            logger.warning("Vector database empty. Populating from CSV data.", "initialize_rag_pipeline")
            print("      ⚠ Vector database is empty")
            print("      → Populating collection from CSV data")
            document_store = DocumentStore(vector_db, config, logger)
            row_records = df.to_dict(orient='records')
            row_ids = [f"row_{idx}" for idx in range(len(row_records))]
            document_store.store_rows(row_records, row_ids)
            collection_count = vector_db.get_collection_count()
            print(f"      ✓ Collection populated with {collection_count} documents")
        else:
            logger.info(f"Vector database has {collection_count} documents", "initialize_rag_pipeline")
            print(f"      ✓ Collection has {collection_count} documents")
        
        # Initialize retriever
        try:
            retriever = get_advanced_retriever(vector_db, config, logger)
            logger.info("Retriever initialized", "initialize_rag_pipeline")
        except Exception as e:
            logger.error(f"Failed to initialize retriever: {str(e)}", "initialize_rag_pipeline")
            raise
        
        # Initialize LLM
        try:
            llm = get_ollama_llm(config, logger)
            logger.info("Ollama LLM initialized", "initialize_rag_pipeline")
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {str(e)}", "initialize_rag_pipeline")
            raise
        
        # Initialize RAG pipeline
        try:
            rag_pipeline = get_rag_pipeline(retriever, llm, config, logger)
            logger.info("RAG pipeline initialized", "initialize_rag_pipeline")
        except Exception as e:
            logger.error(f"Failed to initialize RAG pipeline: {str(e)}", "initialize_rag_pipeline")
            raise
        
        logger.exit_function("initialize_rag_pipeline")
        print("=" * 60)
        print("✓ RAG pipeline initialization completed successfully!")
        print("=" * 60)
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize RAG pipeline: {str(e)}", "initialize_rag_pipeline")
        logger.exit_function("initialize_rag_pipeline")
        print("=" * 60)
        print("✗ RAG pipeline initialization failed!")
        print(f"Error: {str(e)}")
        print("=" * 60)
        return False


@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory('.', 'index.html')


@app.route('/dcc-design-system.css')
def css():
    """Serve the CSS file"""
    return send_from_directory('.', 'dcc-design-system.css')


@app.route('/api/query', methods=['POST'])
def query():
    """
    Handle RAG query requests
    """
    global rag_pipeline
    
    try:
        data = request.json
        query_text = data.get('query', '')
        grouping_strategy = data.get('grouping_strategy', 'none')
        k = data.get('k', 5)
        score_threshold = data.get('score_threshold', 0.0)
        
        if not query_text:
            return jsonify({'error': 'Query text is required'}), 400
        
        logger.info(f"Received query: {query_text[:50]}...", "query")
        
        # Execute query
        if grouping_strategy == 'none':
            result = rag_pipeline.query(
                user_query=query_text,
                k=k,
                score_threshold=score_threshold
            )
        else:
            result = rag_pipeline.query_with_grouping(
                user_query=query_text,
                group_by=grouping_strategy,
                k=k,
                score_threshold=score_threshold
            )
        
        logger.info("Query completed successfully", "query")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Query error: {str(e)}", "query")
        return jsonify({'error': str(e)}), 500


@app.route('/api/status', methods=['GET'])
def status():
    """
    Return system status
    """
    global vector_db, rag_pipeline, embedding_function, llm
    
    try:
        collection_count = vector_db.get_collection_count() if vector_db else 0
        embedding_model = getattr(embedding_function, 'model_name', None)
        llm_model = getattr(llm, 'model_name', None)
        vector_config = vector_db.vector_db_config if vector_db else {}

        return jsonify({
            'status': 'ready' if rag_pipeline else 'not_ready',
            'collection_count': collection_count,
            'data_loaded': collection_count > 0,
            'embedding_file': DATA_PATH.name,
            'embedding_file_path': str(DATA_PATH),
            'embedding_file_status': 'loaded' if DATA_PATH.exists() else 'missing',
            'query_db': vector_config.get('collection_name', 'not_loaded'),
            'query_db_path': vector_config.get('persist_directory', str(VECTOR_DB_PATH)),
            'query_db_status': 'loaded' if collection_count > 0 else 'empty',
            'embedding_model': embedding_model or 'not_loaded',
            'embedding_model_status': 'loaded' if embedding_function else 'not_loaded',
            'explanation_model': llm_model or 'not_loaded',
            'explanation_model_status': get_ollama_status()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


def main():
    """Main entry point"""
    print("\n")
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║           M6 RAG Agent Web Server - Starting...              ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print("\n")
    
    # Initialize RAG pipeline
    if not initialize_rag_pipeline():
        print("\n✗ Failed to initialize RAG pipeline. Exiting.")
        sys.exit(1)
    
    print("\n")
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║           Web Server Starting...                             ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print(f"║  URL: http://localhost:8501                                 ║")
    print(f"║  Press Ctrl+C to stop                                       ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print("\n")
    
    # Run Flask app
    app.run(host='0.0.0.0', port=8501, debug=False)


if __name__ == '__main__':
    main()
