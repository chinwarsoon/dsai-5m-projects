"""
Vector Database Setup using ChromaDB
Implements local vector database for document submittal register
"""

import chromadb
from chromadb.config import Settings
from typing import Dict, Any, List, Optional, Union
from .logger import Logger
from .embeddings import EmbeddingFunction, get_embedding_function


class VectorDatabase:
    """
    Vector database wrapper using ChromaDB
    """
    
    def __init__(self, config: Dict[str, Any], logger: Logger):
        """
        Initialize vector database
        
        Args:
            config: Configuration from schema
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.logger.enter_function("VectorDatabase.__init__")
        
        self.vector_db_config = config.get('vector_db', {})
        self.persist_directory = self.vector_db_config.get('persist_directory')
        self.collection_name = self.vector_db_config.get('collection_name')
        
        self.logger.info(f"Initializing ChromaDB with persist directory: {self.persist_directory}", "VectorDatabase.__init__")
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Use ChromaDB's built-in sentence-transformers embedding function
        from chromadb.utils import embedding_functions
        
        embedding_config = config.get('embeddings', {})
        model_name = embedding_config.get('model_name', 'all-MiniLM-L6-v2')
        
        # Create ChromaDB embedding function
        sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=model_name
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=sentence_transformer_ef
        )
        
        self.logger.info(f"Collection '{self.collection_name}' ready", "VectorDatabase.__init__")
        self.logger.add_trace_entry(
            "collection_name",
            self.collection_name,
            "vector_db_initialization",
            "success"
        )
        
        self.logger.exit_function("VectorDatabase.__init__")
    
    def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ) -> None:
        """
        Add documents to the vector database
        
        Args:
            documents: List of document texts
            metadatas: List of metadata dictionaries
            ids: List of unique document IDs
        """
        self.logger.enter_function("VectorDatabase.add_documents")
        self.logger.info(f"Adding {len(documents)} documents to collection", "VectorDatabase.add_documents")
        
        try:
            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            self.logger.add_trace_entry(
                "documents_added",
                len(documents),
                "vector_db_operation",
                "success"
            )
            
            self.logger.exit_function("VectorDatabase.add_documents")
            
        except Exception as e:
            self.logger.error(f"Failed to add documents: {str(e)}", "VectorDatabase.add_documents")
            self.logger.exit_function("VectorDatabase.add_documents")
    
    def add_embeddings(
        self,
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ) -> None:
        """
        Add pre-computed embeddings to the vector database
        
        Args:
            embeddings: List of embedding vectors
            metadatas: List of metadata dictionaries
            ids: List of unique document IDs
        """
        self.logger.enter_function("VectorDatabase.add_embeddings")
        self.logger.info(f"Adding {len(embeddings)} embeddings to collection", "VectorDatabase.add_embeddings")
        
        try:
            self.collection.add(
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            self.logger.add_trace_entry(
                "embeddings_added",
                len(embeddings),
                "vector_db_operation",
                "success"
            )
            
            self.logger.exit_function("VectorDatabase.add_embeddings")
            
        except Exception as e:
            self.logger.error(f"Failed to add embeddings: {str(e)}", "VectorDatabase.add_embeddings")
            self.logger.exit_function("VectorDatabase.add_embeddings")
    
    def query(
        self,
        query_text: str,
        n_results: int = 10,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Query the vector database
        
        Args:
            query_text: Query text
            n_results: Number of results to return
            where: Metadata filter conditions
            where_document: Document content filter conditions
            
        Returns:
            Query results
        """
        self.logger.enter_function("VectorDatabase.query")
        self.logger.info(f"Querying collection with: {query_text[:50]}...", "VectorDatabase.query")
        
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=where,
                where_document=where_document
            )
            
            self.logger.add_trace_entry(
                "query_results_count",
                len(results.get('ids', [[]])[0]),
                "vector_db_operation",
                "success"
            )
            
            self.logger.exit_function("VectorDatabase.query")
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to query collection: {str(e)}", "VectorDatabase.query")
            self.logger.exit_function("VectorDatabase.query")
            return {}
    
    def query_by_embedding(
        self,
        query_embedding: List[float],
        n_results: int = 10,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Query the vector database using embedding vector
        
        Args:
            query_embedding: Query embedding vector
            n_results: Number of results to return
            where: Metadata filter conditions
            where_document: Document content filter conditions
            
        Returns:
            Query results
        """
        self.logger.enter_function("VectorDatabase.query_by_embedding")
        self.logger.info(f"Querying collection with embedding vector", "VectorDatabase.query_by_embedding")
        
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where,
                where_document=where_document
            )
            
            self.logger.add_trace_entry(
                "query_results_count",
                len(results.get('ids', [[]])[0]),
                "vector_db_operation",
                "success"
            )
            
            self.logger.exit_function("VectorDatabase.query_by_embedding")
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to query collection: {str(e)}", "VectorDatabase.query_by_embedding")
            self.logger.exit_function("VectorDatabase.query_by_embedding")
            return {}
    
    def get_collection_count(self) -> int:
        """
        Get the number of documents in the collection
        
        Returns:
            Document count
        """
        self.logger.enter_function("VectorDatabase.get_collection_count")
        
        try:
            count = self.collection.count()
            self.logger.info(f"Collection has {count} documents", "VectorDatabase.get_collection_count")
            self.logger.exit_function("VectorDatabase.get_collection_count")
            return count
            
        except Exception as e:
            self.logger.error(f"Failed to get collection count: {str(e)}", "VectorDatabase.get_collection_count")
            self.logger.exit_function("VectorDatabase.get_collection_count")
            return 0
    
    def delete_collection(self) -> None:
        """
        Delete the entire collection
        """
        self.logger.enter_function("VectorDatabase.delete_collection")
        self.logger.warning(f"Deleting collection: {self.collection_name}", "VectorDatabase.delete_collection")
        
        try:
            self.client.delete_collection(name=self.collection_name)
            self.logger.info(f"Collection '{self.collection_name}' deleted", "VectorDatabase.delete_collection")
            self.logger.exit_function("VectorDatabase.delete_collection")
            
        except Exception as e:
            self.logger.error(f"Failed to delete collection: {str(e)}", "VectorDatabase.delete_collection")
            self.logger.exit_function("VectorDatabase.delete_collection")


class DocumentStore:
    """
    Document store for managing CSV row records in vector database
    """
    
    def __init__(self, vector_db: VectorDatabase, config: Dict[str, Any], logger: Logger):
        """
        Initialize document store
        
        Args:
            vector_db: Vector database instance
            config: Configuration from schema
            logger: Logger instance
        """
        self.vector_db = vector_db
        self.config = config
        self.logger = logger
        self.logger.enter_function("DocumentStore.__init__")
        
        self.data_columns = config.get('data_columns', [])
        
        self.logger.info("Document store initialized", "DocumentStore.__init__")
        self.logger.exit_function("DocumentStore.__init__")
    
    def store_rows(
        self,
        rows: List[Dict[str, Any]],
        ids: List[str],
        text_column: Optional[str] = None
    ) -> None:
        """
        Store row records in vector database
        
        Args:
            rows: List of row dictionaries
            ids: List of unique IDs for each row
            text_column: Column to use as document text (if None, concatenates all columns)
        """
        self.logger.enter_function("DocumentStore.store_rows")
        self.logger.info(f"Storing {len(rows)} rows in vector database", "DocumentStore.store_rows")
        
        # Convert rows to documents
        documents = []
        metadatas = []
        
        for row in rows:
            if text_column and text_column in row:
                doc_text = str(row[text_column])
            else:
                # Concatenate all columns
                doc_text = " | ".join([f"{k}: {v}" for k, v in row.items() if pd.notna(v)])
            
            documents.append(doc_text)
            metadatas.append(row)
        
        # Add to vector database
        self.vector_db.add_documents(documents, metadatas, ids)
        
        self.logger.exit_function("DocumentStore.store_rows")
    
    def store_rows_with_embeddings(
        self,
        rows: List[Dict[str, Any]],
        embeddings: List[List[float]],
        ids: List[str]
    ) -> None:
        """
        Store row records with pre-computed embeddings
        
        Args:
            rows: List of row dictionaries
            embeddings: List of embedding vectors
            ids: List of unique IDs for each row
        """
        self.logger.enter_function("DocumentStore.store_rows_with_embeddings")
        self.logger.info(f"Storing {len(rows)} rows with embeddings", "DocumentStore.store_rows_with_embeddings")
        
        # Add to vector database with pre-computed embeddings
        self.vector_db.add_embeddings(embeddings, rows, ids)
        
        self.logger.exit_function("DocumentStore.store_rows_with_embeddings")


def get_vector_database(config: Dict[str, Any], logger: Logger) -> VectorDatabase:
    """
    Get vector database instance
    
    Args:
        config: Configuration from schema
        logger: Logger instance
        
    Returns:
        VectorDatabase instance
    """
    return VectorDatabase(config, logger)


# Import pandas for pd.notna check
import pandas as pd
