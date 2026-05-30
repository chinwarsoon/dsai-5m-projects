"""
Query and Retrieval Functions for Document Submittal Register
Implements similarity search and filtering capabilities
"""

from typing import Dict, Any, List, Optional, Union
from .logger import Logger
from .vector_db import VectorDatabase


class Retriever:
    """
    Retriever for querying the vector database
    """
    
    def __init__(self, vector_db: VectorDatabase, config: Dict[str, Any], logger: Logger):
        """
        Initialize retriever
        
        Args:
            vector_db: Vector database instance
            config: Configuration from schema
            logger: Logger instance
        """
        self.vector_db = vector_db
        self.config = config
        self.logger = logger
        self.logger.enter_function("Retriever.__init__")
        
        # Default search parameters
        self.default_k = 10
        self.default_score_threshold = 0.0
        
        self.logger.info("Retriever initialized", "Retriever.__init__")
        self.logger.exit_function("Retriever.__init__")
    
    def query(
        self,
        query_text: str,
        k: int = 10,
        score_threshold: float = 0.0,
        where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Query the vector database with text
        
        Args:
            query_text: Query text
            k: Number of results to return
            score_threshold: Minimum similarity score threshold
            where: Metadata filter conditions
            
        Returns:
            Query results with documents, metadata, and scores
        """
        self.logger.enter_function("Retriever.query")
        self.logger.info(
            f"Querying with k={k}, threshold={score_threshold}",
            "Retriever.query"
        )
        
        # Query vector database
        results = self.vector_db.query(
            query_text=query_text,
            n_results=k,
            where=where
        )
        
        # Filter by score threshold if specified
        if score_threshold > 0 and 'distances' in results:
            filtered_results = self._filter_by_score_threshold(
                results, score_threshold
            )
            self.logger.add_trace_entry(
                "filtered_results_count",
                len(filtered_results.get('ids', [[]])[0]),
                "query_filtering",
                "success"
            )
            results = filtered_results
        
        self.logger.exit_function("Retriever.query")
        return results
    
    def query_by_embedding(
        self,
        query_embedding: List[float],
        k: int = 10,
        score_threshold: float = 0.0,
        where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Query the vector database with embedding vector
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            score_threshold: Minimum similarity score threshold
            where: Metadata filter conditions
            
        Returns:
            Query results with documents, metadata, and scores
        """
        self.logger.enter_function("Retriever.query_by_embedding")
        self.logger.info(
            f"Querying by embedding with k={k}, threshold={score_threshold}",
            "Retriever.query_by_embedding"
        )
        
        # Query vector database
        results = self.vector_db.query_by_embedding(
            query_embedding=query_embedding,
            n_results=k,
            where=where
        )
        
        # Filter by score threshold if specified
        if score_threshold > 0 and 'distances' in results:
            filtered_results = self._filter_by_score_threshold(
                results, score_threshold
            )
            self.logger.add_trace_entry(
                "filtered_results_count",
                len(filtered_results.get('ids', [[]])[0]),
                "query_filtering",
                "success"
            )
            results = filtered_results
        
        self.logger.exit_function("Retriever.query_by_embedding")
        return results
    
    def _filter_by_score_threshold(
        self,
        results: Dict[str, Any],
        threshold: float
    ) -> Dict[str, Any]:
        """
        Filter results by score threshold
        
        Args:
            results: Query results from vector database
            threshold: Minimum similarity score threshold
            
        Returns:
            Filtered results
        """
        self.logger.trace(
            f"Filtering {len(results.get('ids', [[]])[0])} results by threshold {threshold}",
            "Retriever._filter_by_score_threshold"
        )
        
        filtered = {
            'ids': [],
            'documents': [],
            'metadatas': [],
            'distances': []
        }
        
        if 'distances' in results and results['distances']:
            for i, distance in enumerate(results['distances'][0]):
                # Convert distance to similarity score (lower distance = higher similarity)
                # Assuming cosine distance: similarity = 1 - distance
                similarity = 1 - distance
                if similarity >= threshold:
                    filtered['ids'].append(results['ids'][0][i])
                    filtered['documents'].append(results['documents'][0][i])
                    filtered['metadatas'].append(results['metadatas'][0][i])
                    filtered['distances'].append(distance)
        
        return filtered
    
    def filter_by_metadata(
        self,
        results: Dict[str, Any],
        filters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Filter results by metadata conditions
        
        Args:
            results: Query results from vector database
            filters: Metadata filter conditions
            
        Returns:
            Filtered results
        """
        self.logger.enter_function("Retriever.filter_by_metadata")
        self.logger.info(f"Applying metadata filters: {filters}", "Retriever.filter_by_metadata")
        
        filtered = {
            'ids': [],
            'documents': [],
            'metadatas': [],
            'distances': []
        }
        
        if 'metadatas' in results and results['metadatas']:
            for i, metadata in enumerate(results['metadatas'][0]):
                if self._matches_filters(metadata, filters):
                    filtered['ids'].append(results['ids'][0][i])
                    filtered['documents'].append(results['documents'][0][i])
                    filtered['metadatas'].append(metadata)
                    if 'distances' in results:
                        filtered['distances'].append(results['distances'][0][i])
        
        self.logger.add_trace_entry(
            "filtered_results_count",
            len(filtered['ids']),
            "metadata_filtering",
            "success"
        )
        
        self.logger.exit_function("Retriever.filter_by_metadata")
        return filtered
    
    def _matches_filters(self, metadata: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """
        Check if metadata matches filter conditions
        
        Args:
            metadata: Metadata dictionary
            filters: Filter conditions
            
        Returns:
            True if metadata matches all filters, False otherwise
        """
        for key, value in filters.items():
            if key not in metadata:
                return False
            
            if isinstance(value, dict):
                # Handle operators like $eq, $ne, $gt, $lt, etc.
                for op, op_value in value.items():
                    if op == '$eq' and metadata[key] != op_value:
                        return False
                    elif op == '$ne' and metadata[key] == op_value:
                        return False
                    elif op == '$gt' and metadata[key] <= op_value:
                        return False
                    elif op == '$lt' and metadata[key] >= op_value:
                        return False
                    elif op == '$gte' and metadata[key] < op_value:
                        return False
                    elif op == '$lte' and metadata[key] > op_value:
                        return False
                    elif op == '$in' and metadata[key] not in op_value:
                        return False
                    elif op == '$nin' and metadata[key] in op_value:
                        return False
            else:
                # Simple equality check
                if metadata[key] != value:
                    return False
        
        return True
    
    def format_results(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Format query results for display
        
        Args:
            results: Query results from vector database
            
        Returns:
            Formatted results as list of dictionaries
        """
        self.logger.enter_function("Retriever.format_results")
        
        formatted = []
        
        if 'ids' in results and results['ids']:
            for i in range(len(results['ids'][0])):
                formatted_result = {
                    'id': results['ids'][0][i],
                    'document': results['documents'][0][i] if 'documents' in results else None,
                    'metadata': results['metadatas'][0][i] if 'metadatas' in results else None,
                    'distance': results['distances'][0][i] if 'distances' in results else None,
                    'similarity': 1 - results['distances'][0][i] if 'distances' in results else None
                }
                formatted.append(formatted_result)
        
        self.logger.exit_function("Retriever.format_results")
        return formatted


class AdvancedRetriever(Retriever):
    """
    Advanced retriever with additional features
    """
    
    def __init__(self, vector_db: VectorDatabase, config: Dict[str, Any], logger: Logger):
        """
        Initialize advanced retriever
        
        Args:
            vector_db: Vector database instance
            config: Configuration from schema
            logger: Logger instance
        """
        super().__init__(vector_db, config, logger)
        self.logger.enter_function("AdvancedRetriever.__init__")
        
        self.grouping_config = config.get('grouping_strategies', [])
        
        self.logger.exit_function("AdvancedRetriever.__init__")
    
    def query_with_grouping(
        self,
        query_text: str,
        group_by: str,
        k: int = 10,
        score_threshold: float = 0.0
    ) -> Dict[str, Any]:
        """
        Query with grouping by a specific column
        
        Args:
            query_text: Query text
            group_by: Column to group results by
            k: Number of results per group
            score_threshold: Minimum similarity score threshold
            
        Returns:
            Grouped query results
        """
        self.logger.enter_function("AdvancedRetriever.query_with_grouping")
        self.logger.info(f"Querying with grouping by {group_by}", "AdvancedRetriever.query_with_grouping")

        group_column = group_by
        for strategy in self.grouping_config:
            if strategy.get('name') == group_by:
                group_column = strategy.get('column', group_by)
                break
        
        # Get all unique values for the grouping column
        all_results = self.query(query_text, k=k * 10, score_threshold=score_threshold)
        
        # Group results by the specified column
        grouped = {}
        if 'metadatas' in all_results and all_results['metadatas']:
            for i, metadata in enumerate(all_results['metadatas'][0]):
                group_value = metadata.get(group_column, 'unknown')
                if group_value not in grouped:
                    grouped[group_value] = {
                        'ids': [[]],
                        'documents': [[]],
                        'metadatas': [[]],
                        'distances': [[]]
                    }
                
                grouped[group_value]['ids'][0].append(all_results['ids'][0][i])
                grouped[group_value]['documents'][0].append(all_results['documents'][0][i])
                grouped[group_value]['metadatas'][0].append(metadata)
                grouped[group_value]['distances'][0].append(all_results['distances'][0][i])
        
        # Limit results per group
        for group in grouped:
            grouped[group]['ids'][0] = grouped[group]['ids'][0][:k]
            grouped[group]['documents'][0] = grouped[group]['documents'][0][:k]
            grouped[group]['metadatas'][0] = grouped[group]['metadatas'][0][:k]
            grouped[group]['distances'][0] = grouped[group]['distances'][0][:k]
        
        self.logger.add_trace_entry(
            "groups_found",
            len(grouped),
            "grouping_query",
            "success"
        )
        
        self.logger.exit_function("AdvancedRetriever.query_with_grouping")
        return grouped
    
    def hybrid_search(
        self,
        query_text: str,
        metadata_filters: Dict[str, Any],
        k: int = 10,
        score_threshold: float = 0.0
    ) -> Dict[str, Any]:
        """
        Hybrid search combining semantic search with metadata filtering
        
        Args:
            query_text: Query text
            metadata_filters: Metadata filter conditions
            k: Number of results to return
            score_threshold: Minimum similarity score threshold
            
        Returns:
            Hybrid search results
        """
        self.logger.enter_function("AdvancedRetriever.hybrid_search")
        self.logger.info("Performing hybrid search", "AdvancedRetriever.hybrid_search")
        
        # First, query with metadata filters
        results = self.query(
            query_text=query_text,
            k=k,
            score_threshold=score_threshold,
            where=metadata_filters
        )
        
        # Apply additional metadata filtering if needed
        filtered_results = self.filter_by_metadata(results, metadata_filters)
        
        self.logger.exit_function("AdvancedRetriever.hybrid_search")
        return filtered_results


def get_retriever(vector_db: VectorDatabase, config: Dict[str, Any], logger: Logger) -> Retriever:
    """
    Get retriever instance
    
    Args:
        vector_db: Vector database instance
        config: Configuration from schema
        logger: Logger instance
        
    Returns:
        Retriever instance
    """
    return Retriever(vector_db, config, logger)


def get_advanced_retriever(vector_db: VectorDatabase, config: Dict[str, Any], logger: Logger) -> AdvancedRetriever:
    """
    Get advanced retriever instance
    
    Args:
        vector_db: Vector database instance
        config: Configuration from schema
        logger: Logger instance
        
    Returns:
        AdvancedRetriever instance
    """
    return AdvancedRetriever(vector_db, config, logger)
