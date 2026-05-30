"""
Chunking Strategy Module for Document Submittal Register
Implements multiple chunking strategies for optimized document representation
in the vector database. Supports automatic strategy selection based on data source.
"""

import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from .logger import Logger


class ChunkingStrategy:
    """Base class for chunking strategies"""

    def __init__(self, name: str, config: Dict[str, Any], logger: Logger):
        self.name = name
        self.config = config
        self.logger = logger
        self.logger.enter_function(f"ChunkingStrategy.__init__.{name}")
        self.logger.exit_function(f"ChunkingStrategy.__init__.{name}")

    def chunk_row(self, row: Dict[str, Any], row_index: int) -> List[Dict[str, Any]]:
        raise NotImplementedError("Subclasses must implement chunk_row")

    def chunk_rows(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        self.logger.enter_function(f"ChunkingStrategy.chunk_rows.{self.name}")
        self.logger.info(f"Chunking {len(rows)} rows with {self.name} strategy", f"ChunkingStrategy.chunk_rows.{self.name}")
        all_chunks = []
        for i, row in enumerate(rows):
            chunks = self.chunk_row(row, i)
            all_chunks.extend(chunks)
        self.logger.add_trace_entry(
            f"{self.name}_chunks_total",
            len(all_chunks),
            "chunking_operation",
            "success"
        )
        self.logger.exit_function(f"ChunkingStrategy.chunk_rows.{self.name}")
        return all_chunks


class RowLevelChunking(ChunkingStrategy):
    """Entire row as a single document chunk"""

    def __init__(self, config: Dict[str, Any], logger: Logger):
        super().__init__("row_level", config, logger)

    def chunk_row(self, row: Dict[str, Any], row_index: int) -> List[Dict[str, Any]]:
        text_parts = []
        for key, value in row.items():
            if pd.notna(value):
                text_parts.append(f"{key}: {value}")
        doc_text = " | ".join(text_parts)
        return [{
            "text": doc_text,
            "metadata": {
                **row,
                "chunk_type": "row_level",
                "chunk_index": 0,
                "parent_row_index": row_index
            },
            "id": f"row_{row_index}"
        }]


class StructuredChunking(ChunkingStrategy):
    """Split row into semantic chunks by column groups defined in config"""

    def __init__(self, config: Dict[str, Any], logger: Logger):
        super().__init__("structured", config, logger)
        self.column_groups = []
        strategies = config.get('chunking', {}).get('strategies', {})
        structured_config = strategies.get('structured', {})
        self.column_groups = structured_config.get('column_groups', [])
        self.logger.info(
            f"Initialized structured chunking with {len(self.column_groups)} column groups",
            "StructuredChunking.__init__"
        )

    def chunk_row(self, row: Dict[str, Any], row_index: int) -> List[Dict[str, Any]]:
        chunks = []
        for gi, group in enumerate(self.column_groups):
            group_name = group.get('name', f'group_{gi}')
            group_columns = group.get('columns', [])
            text_parts = []
            group_metadata = {"parent_row_index": row_index}
            has_data = False
            for col in group_columns:
                if col in row and pd.notna(row[col]):
                    text_parts.append(f"{col}: {row[col]}")
                    group_metadata[col] = row[col]
                    has_data = True
            if not has_data:
                continue
            doc_text = " | ".join(text_parts)
            chunks.append({
                "text": doc_text,
                "metadata": {
                    **row,
                    "chunk_type": "structured",
                    "chunk_group": group_name,
                    "chunk_index": gi,
                    "parent_row_index": row_index
                },
                "id": f"row_{row_index}_chunk_{gi}"
            })
        return chunks


class SemanticChunking(ChunkingStrategy):
    """Split based on semantic boundaries (placeholder for future)"""

    def __init__(self, config: Dict[str, Any], logger: Logger):
        super().__init__("semantic", config, logger)
        strategies = config.get('chunking', {}).get('strategies', {})
        semantic_config = strategies.get('semantic', {})
        self.min_chunk_size = semantic_config.get('min_chunk_size', 200)
        self.max_chunk_size = semantic_config.get('max_chunk_size', 500)

    def chunk_row(self, row: Dict[str, Any], row_index: int) -> List[Dict[str, Any]]:
        text_parts = []
        for key, value in row.items():
            if pd.notna(value):
                text_parts.append(f"{key}: {value}")
        full_text = " | ".join(text_parts)
        chunks = []
        if len(full_text) <= self.max_chunk_size:
            return [{
                "text": full_text,
                "metadata": {
                    **row,
                    "chunk_type": "semantic",
                    "chunk_index": 0,
                    "parent_row_index": row_index
                },
                "id": f"row_{row_index}"
            }]
        start = 0
        ci = 0
        while start < len(full_text):
            end = min(start + self.max_chunk_size, len(full_text))
            chunk_text = full_text[start:end]
            chunks.append({
                "text": chunk_text,
                "metadata": {
                    **row,
                    "chunk_type": "semantic",
                    "chunk_index": ci,
                    "parent_row_index": row_index
                },
                "id": f"row_{row_index}_chunk_{ci}"
            })
            start = end
            ci += 1
        return chunks


class ChunkingManager:
    """Manager for all chunking strategies with automatic selection"""

    def __init__(self, config: Dict[str, Any], logger: Logger):
        self.logger = logger
        self.logger.enter_function("ChunkingManager.__init__")
        self.config = config
        self.strategies: Dict[str, ChunkingStrategy] = {}
        chunking_config = config.get('chunking', {})
        strategies_config = chunking_config.get('strategies', {})
        for name, strategy_cfg in strategies_config.items():
            if strategy_cfg.get('enabled', False):
                self.strategies[name] = self._create_strategy(name)
                self.logger.info(f"Initialized chunking strategy: {name}", "ChunkingManager.__init__")
        self.logger.add_trace_entry(
            "enabled_chunking_strategies",
            list(self.strategies.keys()),
            "chunking_initialization",
            "success"
        )
        self.logger.exit_function("ChunkingManager.__init__")

    def _create_strategy(self, name: str) -> ChunkingStrategy:
        if name == "row_level":
            return RowLevelChunking(self.config, self.logger)
        elif name == "structured":
            return StructuredChunking(self.config, self.logger)
        elif name == "semantic":
            return SemanticChunking(self.config, self.logger)
        else:
            self.logger.warning(f"Unknown chunking strategy: {name}", "ChunkingManager._create_strategy")
            return RowLevelChunking(self.config, self.logger)

    def get_strategy(self, name: str) -> Optional[ChunkingStrategy]:
        return self.strategies.get(name)

    def chunk_rows_with_strategy(self, rows: List[Dict[str, Any]], strategy_name: str) -> List[Dict[str, Any]]:
        self.logger.enter_function("ChunkingManager.chunk_rows_with_strategy")
        strategy = self.get_strategy(strategy_name)
        if not strategy:
            self.logger.warning(f"Strategy {strategy_name} not found, using row_level", "ChunkingManager.chunk_rows_with_strategy")
            strategy = self.get_strategy("row_level")
        if not strategy:
            self.logger.error("No fallback strategy available", "ChunkingManager.chunk_rows_with_strategy")
            self.logger.exit_function("ChunkingManager.chunk_rows_with_strategy")
            return []
        result = strategy.chunk_rows(rows)
        self.logger.exit_function("ChunkingManager.chunk_rows_with_strategy")
        return result

    def get_enabled_strategies(self) -> List[str]:
        return list(self.strategies.keys())


def get_chunking_manager(config: Dict[str, Any], logger: Logger) -> ChunkingManager:
    return ChunkingManager(config, logger)
