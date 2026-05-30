"""
M6 RAG Agent Web Server
Serves the HTML interface and provides API endpoints for RAG queries
"""

import sys
import os
import json
import uuid
import time
import threading
import shutil
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

# Rebuild task tracking
rebuild_tasks: dict = {}
rebuild_lock = threading.Lock()


def _update_rebuild_progress(task_id: str, **kwargs):
    """Thread-safe update of rebuild progress."""
    with rebuild_lock:
        if task_id in rebuild_tasks:
            rebuild_tasks[task_id].update(kwargs)
            rebuild_tasks[task_id]['timestamp'] = time.time()


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
        chunking_strategy = data.get('chunking_strategy', None)
        k = data.get('k', 5)
        score_threshold = data.get('score_threshold', 0.0)
        
        if not query_text:
            return jsonify({'error': 'Query text is required'}), 400
        
        logger.info(f"Received query: {query_text[:50]}...", "query")
        
        # Set chunking strategy on retriever if provided
        if chunking_strategy and hasattr(retriever, 'set_chunking_strategy'):
            retriever.set_chunking_strategy(chunking_strategy)
        
        # Execute query
        if grouping_strategy == 'none':
            result = rag_pipeline.query(
                user_query=query_text,
                k=k,
                score_threshold=score_threshold,
                chunking_strategy=chunking_strategy
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

        chunking_strategy = rag_pipeline.get_chunking_strategy() if rag_pipeline else 'not_loaded'
        
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
            'explanation_model_status': get_ollama_status(),
            'chunking_strategy': chunking_strategy
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@app.route('/api/upload', methods=['POST'])
def upload():
    """
    Upload a CSV file for vector database rebuild.
    Saves to data/ directory and returns the filename.
    """
    global logger

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'Only CSV files are supported'}), 400

    try:
        data_dir = Path(__file__).parent.parent / 'data'
        data_dir.mkdir(parents=True, exist_ok=True)
        save_path = data_dir / file.filename
        file.save(str(save_path))
        logger.info(f"File uploaded: {file.filename} ({save_path})", "upload")
        return jsonify({
            'success': True,
            'filename': file.filename,
            'path': str(save_path),
            'message': f"File {file.filename} uploaded successfully"
        })
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}", "upload")
        return jsonify({'error': str(e)}), 500


@app.route('/api/rebuild', methods=['POST'])
def rebuild():
    """
    Start rebuilding the vector database asynchronously.
    Returns a task_id for polling progress via /api/rebuild-status/<task_id>.
    """
    global rebuild_tasks

    data = request.json or {}
    filename = data.get('filename', 'processed_dcc_universal.csv')
    chunking_strategy = data.get('chunking_strategy', 'row_level')

    data_dir = Path(__file__).parent.parent / 'data'
    csv_path = data_dir / filename

    if not csv_path.exists():
        return jsonify({'error': f'File {filename} not found in data directory'}), 404

    task_id = str(uuid.uuid4())
    rebuild_tasks[task_id] = {
        'task_id': task_id,
        'status': 'starting',
        'progress': 0,
        'filename': filename,
        'chunking_strategy': chunking_strategy,
        'steps': [],
        'error': None,
        'timestamp': time.time()
    }

    thread = threading.Thread(
        target=_run_rebuild,
        args=(task_id, filename, chunking_strategy),
        daemon=True
    )
    thread.start()

    return jsonify({
        'task_id': task_id,
        'status': 'started',
        'message': f"Rebuild started for {filename}"
    })


def _run_rebuild(task_id: str, filename: str, chunking_strategy: str):
    """Run rebuild in background thread with progress updates."""
    global logger, vector_db, retriever, rag_pipeline, embedding_function

    def progress(**kw):
        _update_rebuild_progress(task_id, **kw)

    def add_step(name: str, pct: int, detail: str = ""):
        step = {
            'name': name,
            'progress': pct,
            'detail': detail,
            'status': 'running',
            'timestamp': time.time()
        }
        progress(
            status='running',
            progress=pct,
            current_step=name,
            steps=rebuild_tasks.get(task_id, {}).get('steps', []) + [step]
        )

    def complete_step(name: str, pct: int, detail: str = ""):
        steps = list(rebuild_tasks.get(task_id, {}).get('steps', []))
        if steps:
            steps[-1]['status'] = 'completed'
        steps.append({
            'name': name,
            'progress': pct,
            'detail': detail,
            'status': 'completed',
            'timestamp': time.time()
        })
        progress(status='running', progress=pct, current_step=name, steps=steps)

    def fail_step(error_msg: str):
        steps = list(rebuild_tasks.get(task_id, {}).get('steps', []))
        if steps:
            steps[-1]['status'] = 'error'
        progress(status='error', error=error_msg, steps=steps)

    try:
        add_step("Loading configuration", 5)
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
        complete_step("Configuration loaded", 10, f"Source: {CONFIG_PATH.name}")

        add_step(f"Loading CSV: {filename}", 15)
        csv_path = Path(__file__).parent.parent / 'data' / filename
        csv_loader = CSVLoader(config, logger)
        df = csv_loader.load_csv(str(csv_path))
        df = csv_loader.process_by_priority(df)
        row_count = len(df)
        complete_step(f"CSV loaded: {row_count} rows", 25, f"File: {filename}, Rows: {row_count}")

        add_step("Initializing embedding function", 30)
        embedding_function = get_embedding_function(config, logger)
        embedding_model = getattr(embedding_function, 'model_name', 'all-MiniLM-L6-v2')
        complete_step(f"Embedding model: {embedding_model}", 35)

        add_step("Connecting to vector database", 40)
        if vector_db:
            try:
                vector_db.delete_collection()
            except Exception:
                pass
            vector_db.collection = vector_db.client.get_or_create_collection(
                name=vector_db.collection_name,
                embedding_function=vector_db.collection._embedding_function
            )
        else:
            vector_db = get_vector_database(config, logger, embedding_function)
        complete_step("Vector database ready", 45)

        row_records = df.to_dict(orient='records')
        total = len(row_records)
        document_store = DocumentStore(vector_db, config, logger)

        if chunking_strategy and chunking_strategy != 'row_level':
            add_step(
                f"Chunking {total} rows using {chunking_strategy} strategy",
                50,
                f"Strategy: {chunking_strategy}"
            )
            from engine.chunking import get_chunking_manager
            chunking_manager = get_chunking_manager(config, logger)
            chunks = chunking_manager.chunk_rows_with_strategy(row_records, chunking_strategy)
            chunk_count = len(chunks)
            complete_step(
                f"Chunking complete: {chunk_count} chunks created",
                65,
                f"Strategy: {chunking_strategy}, Chunks: {chunk_count}"
            )

            add_step(f"Storing {chunk_count} chunks in vector database", 70)
            document_store.store_structured_chunks(chunks)
            complete_step("Chunks stored in database", 85)
        else:
            add_step(f"Preparing {total} row documents", 50)
            row_ids = [f"row_{idx}" for idx in range(total)]
            complete_step("Row documents prepared", 60)

            add_step(f"Storing {total} rows in vector database", 65)
            document_store.store_rows(row_records, row_ids)
            complete_step("Rows stored in database", 85)

        collection_count = vector_db.get_collection_count()
        logger.info(f"Collection has {collection_count} documents after rebuild", "rebuild")

        add_step("Reinitializing retriever and RAG pipeline", 90)
        retriever = get_advanced_retriever(vector_db, config, logger)
        llm = get_ollama_llm(config, logger)
        rag_pipeline = get_rag_pipeline(retriever, llm, config, logger)
        complete_step("RAG pipeline ready", 100)

        progress(
            status='completed',
            progress=100,
            current_step='Complete',
            collection_count=collection_count,
            rows_loaded=row_count
        )
        logger.info(
            f"Rebuild complete: {collection_count} documents using {chunking_strategy}",
            "rebuild"
        )

    except Exception as e:
        logger.error(f"Rebuild failed: {str(e)}", "rebuild")
        fail_step(str(e))


@app.route('/api/rebuild-status/<task_id>', methods=['GET'])
def rebuild_status(task_id: str):
    """Return current rebuild progress for the given task_id."""
    with rebuild_lock:
        task = rebuild_tasks.get(task_id)
        if task is None:
            return jsonify({'error': 'Task not found'}), 404

        status = task.get('status', 'unknown')
        result = {
            'task_id': task_id,
            'status': status,
            'progress': task.get('progress', 0),
            'current_step': task.get('current_step', ''),
            'filename': task.get('filename', ''),
            'chunking_strategy': task.get('chunking_strategy', ''),
            'steps': task.get('steps', []),
            'collection_count': task.get('collection_count', 0),
            'rows_loaded': task.get('rows_loaded', 0),
            'error': task.get('error'),
        }

        if status in ('completed', 'error'):
            del rebuild_tasks[task_id]

        return jsonify(result)


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
