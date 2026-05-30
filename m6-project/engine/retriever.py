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
    Supports structured chunk hierarchy awareness and chunk aggregation
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
        self.chunking_config = config.get('chunking', {})
        self.selected_strategy = None
        
        self.logger.exit_function("AdvancedRetriever.__init__")

    def set_chunking_strategy(self, strategy_name: str) -> None:
        """
        Set the chunking strategy for retrieval operations.
        
        Args:
            strategy_name: Name of chunking strategy
        """
        self.selected_strategy = strategy_name
        self.logger.info(f"Chunking strategy set to: {strategy_name}", "AdvancedRetriever.set_chunking_strategy")

    def query_with_chunking(
        self,
        query_text: str,
        k: int = 10,
        score_threshold: float = 0.0,
        where: Optional[Dict[str, Any]] = None,
        chunking_strategy: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Query with awareness of chunking strategy.
        For structured chunks, aggregates related chunks to provide full row context.

        Args:
            query_text: Query text
            k: Number of results to return
            score_threshold: Minimum similarity score threshold
            where: Metadata filter conditions
            chunking_strategy: Chunking strategy name for awareness logic

        Returns:
            Query results with optional aggregation
        """
        self.logger.enter_function("AdvancedRetriever.query_with_chunking")
        self.logger.info(
            f"Querying with chunking strategy: {chunking_strategy or self.selected_strategy or 'none'}",
            "AdvancedRetriever.query_with_chunking"
        )
        
        results = super().query(
            query_text=query_text,
            k=k,
            score_threshold=score_threshold,
            where=where
        )
        
        strategy = chunking_strategy or self.selected_strategy
        if strategy == "structured":
            results = self._aggregate_structured_chunks(results)
            results = self._deduplicate_by_parent_row(results)
        
        self.logger.add_trace_entry(
            "query_with_chunking_results",
            len(results.get('ids', [[]])[0]) if results.get('ids') else 0,
            "advanced_retrieval",
            "success"
        )
        
        self.logger.exit_function("AdvancedRetriever.query_with_chunking")
        return results

    def _deduplicate_by_parent_row(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deduplicate results by parent_row_index, keeping the best scoring chunk per row.
        
        Args:
            results: Query results
            
        Returns:
            Deduplicated results
        """
        if not results.get('ids'):
            return results
        
        seen_rows = {}
        for i in range(len(results['ids'][0])):
            metadata = results['metadatas'][0][i] if results.get('metadatas') else {}
            parent_idx = metadata.get('parent_row_index', i)
            distance = results['distances'][0][i] if results.get('distances') else 0
            
            if parent_idx not in seen_rows or distance < seen_rows[parent_idx]['distance']:
                seen_rows[parent_idx] = {
                    'index': i,
                    'distance': distance
                }
        
        deduped = {
            'ids': [[]],
            'documents': [[]],
            'metadatas': [[]],
            'distances': [[]]
        }
        sorted_entries = sorted(seen_rows.values(), key=lambda x: x['distance'])
        for entry in sorted_entries:
            i = entry['index']
            deduped['ids'][0].append(results['ids'][0][i])
            if results.get('documents'):
                deduped['documents'][0].append(results['documents'][0][i])
            if results.get('metadatas'):
                deduped['metadatas'][0].append(results['metadatas'][0][i])
            if results.get('distances'):
                deduped['distances'][0].append(results['distances'][0][i])
        
        return deduped

    def _aggregate_structured_chunks(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aggregate related structured chunks to provide full row context.
        When multiple chunks from the same parent row are retrieved,
        combine them into a single result with richer context.

        Args:
            results: Query results from vector database

        Returns:
            Aggregated results with combined row context
        """
        if not results.get('ids') or not results.get('metadatas'):
            return results
        
        row_groups = {}
        chunk_types = {}
        
        for i in range(len(results['ids'][0])):
            chunk_id = results['ids'][0][i]
            metadata = results['metadatas'][0][i]
            document = results['documents'][0][i] if results.get('documents') else ""
            distance = results['distances'][0][i] if results.get('distances') else 0
            
            parent_idx = metadata.get('parent_row_index', i)
            chunk_type = metadata.get('chunk_type', 'row_level')
            chunk_group = metadata.get('chunk_group', 'unknown')
            
            if parent_idx not in row_groups:
                row_groups[parent_idx] = {
                    'ids': [],
                    'documents': [],
                    'metadatas': [],
                    'distances': [],
                    'chunk_groups': set(),
                    'min_distance': distance
                }
            
            row_groups[parent_idx]['ids'].append(chunk_id)
            row_groups[parent_idx]['documents'].append(document)
            row_groups[parent_idx]['metadatas'].append(metadata)
            row_groups[parent_idx]['distances'].append(distance)
            row_groups[parent_idx]['chunk_groups'].add(chunk_group)
            row_groups[parent_idx]['min_distance'] = min(
                row_groups[parent_idx]['min_distance'], distance
            )
            chunk_types[parent_idx] = chunk_type
        
        aggregated = {
            'ids': [[]],
            'documents': [[]],
            'metadatas': [[]],
            'distances': [[]]
        }
        
        sorted_rows = sorted(row_groups.items(), key=lambda x: x[1]['min_distance'])
        for parent_idx, group in sorted_rows:
            aggregated['ids'][0].append(f"aggregated_row_{parent_idx}")
            
            combined_text = " | ".join(group['documents'])
            aggregated['documents'][0].append(combined_text)
            
            combined_metadata = {}
            for md in group['metadatas']:
                combined_metadata.update(md)
            combined_metadata['aggregated'] = True
            combined_metadata['aggregated_chunks'] = len(group['ids'])
            combined_metadata['chunk_types'] = list(group['chunk_groups'])
            aggregated['metadatas'][0].append(combined_metadata)
            
            aggregated['distances'][0].append(group['min_distance'])
        
        self.logger.add_trace_entry(
            "aggregated_chunks_count",
            len(aggregated['ids'][0]),
            "chunk_aggregation",
            "success"
        )
        
        return aggregated
    
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
