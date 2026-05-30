"""
Vector Database Setup using ChromaDB
Implements local vector database for document submittal register
"""

import chromadb
import pandas as pd
from chromadb.config import Settings
from typing import Dict, Any, List, Optional, Union
from .logger import Logger
from .embeddings import EmbeddingFunction, get_embedding_function


class ChromaLocalEmbeddingFunction:
    """Adapter so ChromaDB uses the project's local embedding instance."""

    def __init__(self, embedding_function: EmbeddingFunction):
        self.embedding_function = embedding_function

    def name(self) -> str:
        return "m6-local-sentence-transformer"

    def __call__(self, input):
        return self.embedding_function.embed_texts(list(input))

    def embed_query(self, input):
        return self.embedding_function.embed_text(input)

    def embed_documents(self, input):
        return self.embedding_function.embed_texts(list(input))


class VectorDatabase:
    """
    Vector database wrapper using ChromaDB
    """
    
    def __init__(
        self,
        config: Dict[str, Any],
        logger: Logger,
        embedding_function: Optional[EmbeddingFunction] = None
    ):
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
        
        if embedding_function is None:
            embedding_function = get_embedding_function(config, logger)

        chroma_embedding_function = ChromaLocalEmbeddingFunction(embedding_function)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=chroma_embedding_function
        )
        
        self.logger.info(f"Collection '{self.collection_name}' ready", "VectorDatabase.__init__")
        self.logger.add_trace_entry(
            "collection_name",
            self.collection_name,
            "vector_db_initialization",
            "success"
        )
        
        self.logger.exit_function("VectorDatabase.__init__")

    def _clean_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert row metadata to ChromaDB-compatible scalar values.
        """
        cleaned = {}
        for key, value in metadata.items():
            if pd.isna(value):
                continue
            if hasattr(value, "item"):
                value = value.item()
            if isinstance(value, (str, int, float, bool)):
                cleaned[key] = value
            else:
                cleaned[key] = str(value)
        return cleaned

    def _add_in_batches(self, batch_size: int = 500, **kwargs) -> None:
        total = len(kwargs["ids"])
        for start in range(0, total, batch_size):
            end = start + batch_size
            batch = {
                key: value[start:end]
                for key, value in kwargs.items()
                if value is not None
            }
            self.collection.add(**batch)
    
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
            clean_metadatas = [self._clean_metadata(metadata) for metadata in metadatas]
            self._add_in_batches(
                documents=documents,
                metadatas=clean_metadatas,
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
            clean_metadatas = [self._clean_metadata(metadata) for metadata in metadatas]
            self._add_in_batches(
                embeddings=embeddings,
                metadatas=clean_metadatas,
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


def get_vector_database(
    config: Dict[str, Any],
    logger: Logger,
    embedding_function: Optional[EmbeddingFunction] = None
) -> VectorDatabase:
    """
    Get vector database instance
    
    Args:
        config: Configuration from schema
        logger: Logger instance
        
    Returns:
        VectorDatabase instance
    """
    return VectorDatabase(config, logger, embedding_function)
