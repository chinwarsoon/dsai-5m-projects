"""
Embedding Functions for Document Submittal Register
Implements local embeddings using sentence-transformers
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Union
from sentence_transformers import SentenceTransformer
from .logger import Logger


class EmbeddingFunction:
    """
    Base embedding function class
    """
    
    def __init__(self, config: Dict[str, Any], logger: Logger):
        """
        Initialize embedding function
        
        Args:
            config: Configuration from schema
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.logger.enter_function("EmbeddingFunction.__init__")
        
        self.embedding_config = config.get('embeddings', {})
        self.model_name = self.embedding_config.get('model_name', 'all-MiniLM-L6-v2')
        self.local_files_only = self.embedding_config.get('local_files_only', True)
        
        self.logger.info(f"Initializing embedding model: {self.model_name}", "EmbeddingFunction.__init__")
        self.logger.add_trace_entry(
            "embedding_model",
            self.model_name,
            "embedding_initialization",
            "success"
        )
        
        self.logger.exit_function("EmbeddingFunction.__init__")
    
    def embed_text(self, text: str) -> List[float]:
        """
        Embed a single text string
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        self.logger.enter_function("EmbeddingFunction.embed_text")
        self.logger.trace(f"Embedding text (length: {len(text)})", "EmbeddingFunction.embed_text")
        
        raise NotImplementedError("Subclasses must implement embed_text")
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Embed multiple text strings
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        self.logger.enter_function("EmbeddingFunction.embed_texts")
        self.logger.info(f"Embedding {len(texts)} texts", "EmbeddingFunction.embed_texts")
        
        raise NotImplementedError("Subclasses must implement embed_texts")
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of the embedding vectors
        
        Returns:
            Embedding dimension
        """
        raise NotImplementedError("Subclasses must implement get_embedding_dimension")


class SentenceTransformerEmbedding(EmbeddingFunction):
    """
    Embedding function using sentence-transformers
    """
    
    def __init__(self, config: Dict[str, Any], logger: Logger):
        """
        Initialize sentence-transformers embedding
        
        Args:
            config: Configuration from schema
            logger: Logger instance
        """
        super().__init__(config, logger)
        self.logger.enter_function("SentenceTransformerEmbedding.__init__")
        
        self.name = "sentence-transformers"
        
        try:
            self.model = SentenceTransformer(
                self.model_name,
                local_files_only=self.local_files_only
            )
            self.embedding_dimension = self.model.get_embedding_dimension()
            
            self.logger.info(
                f"Loaded model {self.model_name} with dimension {self.embedding_dimension}",
                "SentenceTransformerEmbedding.__init__"
            )
            self.logger.add_trace_entry(
                "embedding_dimension",
                self.embedding_dimension,
                "model_loading",
                "success"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to load embedding model: {str(e)}", "SentenceTransformerEmbedding.__init__")
            self.logger.fail_fast(f"Embedding model load failed: {str(e)}", "SentenceTransformerEmbedding.__init__")
        
        self.logger.exit_function("SentenceTransformerEmbedding.__init__")
    
    def embed_text(self, text: str) -> List[float]:
        """
        Embed a single text string
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        self.logger.enter_function("SentenceTransformerEmbedding.embed_text")
        self.logger.trace(f"Embedding text (length: {len(text)})", "SentenceTransformerEmbedding.embed_text")
        
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            result = embedding.tolist()
            
            self.logger.add_trace_entry(
                "embedding_vector_length",
                len(result),
                "embedding_operation",
                "success"
            )
            
            self.logger.exit_function("SentenceTransformerEmbedding.embed_text")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to embed text: {str(e)}", "SentenceTransformerEmbedding.embed_text")
            self.logger.exit_function("SentenceTransformerEmbedding.embed_text")
            return []
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Embed multiple text strings
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        self.logger.enter_function("SentenceTransformerEmbedding.embed_texts")
        self.logger.info(f"Embedding {len(texts)} texts", "SentenceTransformerEmbedding.embed_texts")
        
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            result = embeddings.tolist()
            
            self.logger.add_trace_entry(
                "embeddings_count",
                len(result),
                "batch_embedding_operation",
                "success"
            )
            
            self.logger.exit_function("SentenceTransformerEmbedding.embed_texts")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to embed texts: {str(e)}", "SentenceTransformerEmbedding.embed_texts")
            self.logger.exit_function("SentenceTransformerEmbedding.embed_texts")
            return []
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of the embedding vectors
        
        Returns:
            Embedding dimension
        """
        return self.embedding_dimension


class RowRecordEmbedder:
    """
    Embedder for CSV row records
    Converts row data to text and embeds it
    """
    
    def __init__(self, embedding_function: EmbeddingFunction, config: Dict[str, Any], logger: Logger):
        """
        Initialize row record embedder
        
        Args:
            embedding_function: Embedding function to use
            config: Configuration from schema
            logger: Logger instance
        """
        self.embedding_function = embedding_function
        self.config = config
        self.logger = logger
        self.logger.enter_function("RowRecordEmbedder.__init__")
        
        self.data_columns = config.get('data_columns', [])
        
        # Identify columns to include in embeddings (Priority 1 and 2)
        self.embedding_columns = []
        for col_config in self.data_columns:
            col_name = col_config.get('name')
            priority = col_config.get('priority')
            if priority in [1, 2]:
                self.embedding_columns.append(col_name)
        
        self.logger.info(
            f"Initialized row embedder with {len(self.embedding_columns)} columns",
            "RowRecordEmbedder.__init__"
        )
        self.logger.add_trace_entry(
            "embedding_columns_count",
            len(self.embedding_columns),
            "embedder_initialization",
            "success"
        )
        
        self.logger.exit_function("RowRecordEmbedder.__init__")
    
    def row_to_text(self, row: Dict[str, Any]) -> str:
        """
        Convert a row dictionary to text string for embedding
        
        Args:
            row: Row data as dictionary
            
        Returns:
            Text representation of the row
        """
        self.logger.trace("Converting row to text", "RowRecordEmbedder.row_to_text")
        
        text_parts = []
        for col in self.embedding_columns:
            if col in row:
                value = row[col]
                if pd.notna(value):
                    text_parts.append(f"{col}: {value}")
        
        return " | ".join(text_parts)
    
    def embed_row(self, row: Dict[str, Any]) -> List[float]:
        """
        Embed a single row record
        
        Args:
            row: Row data as dictionary
            
        Returns:
            Embedding vector
        """
        self.logger.enter_function("RowRecordEmbedder.embed_row")
        
        text = self.row_to_text(row)
        if not text:
            self.logger.warning("Empty text for embedding", "RowRecordEmbedder.embed_row")
            self.logger.exit_function("RowRecordEmbedder.embed_row")
            return []
        
        embedding = self.embedding_function.embed_text(text)
        
        self.logger.exit_function("RowRecordEmbedder.embed_row")
        return embedding
    
    def embed_rows(self, rows: List[Dict[str, Any]]) -> List[List[float]]:
        """
        Embed multiple row records
        
        Args:
            rows: List of row data as dictionaries
            
        Returns:
            List of embedding vectors
        """
        self.logger.enter_function("RowRecordEmbedder.embed_rows")
        self.logger.info(f"Embedding {len(rows)} rows", "RowRecordEmbedder.embed_rows")
        
        texts = [self.row_to_text(row) for row in rows]
        texts = [t for t in texts if t]  # Filter empty texts
        
        embeddings = self.embedding_function.embed_texts(texts)
        
        self.logger.exit_function("RowRecordEmbedder.embed_rows")
        return embeddings


def get_embedding_function(config: Dict[str, Any], logger: Logger) -> EmbeddingFunction:
    """
    Get embedding function instance based on configuration
    
    Args:
        config: Configuration from schema
        logger: Logger instance
        
    Returns:
        Embedding function instance
    """
    vector_db_config = config.get('vector_db', {})
    embedding_model = vector_db_config.get('embedding_model', 'all-MiniLM-L6-v2')
    
    if 'sentence-transformers' in embedding_model or 'MiniLM' in embedding_model:
        return SentenceTransformerEmbedding(config, logger)
    else:
        logger.warning(f"Unknown embedding model: {embedding_model}, using default", "get_embedding_function")
        return SentenceTransformerEmbedding(config, logger)


# Import pandas for pd.notna check
import pandas as pd
