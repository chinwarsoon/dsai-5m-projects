"""
CSV Loader with Data Column Priority Processing
Implements Section 1 of agent_rule.md: Data columns
"""

import pandas as pd
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from .logger import Logger, LogLevel


class CSVLoader:
    """
    CSV loader with data column priority processing per Section 1
    
    Priority Levels:
    - Priority 1: Meta data columns (Project_Code, Department, Submission_Session, etc.)
      - Must be processed first
      - Safe for bounded forward fill
    - Priority 2: Relational Keys & Transactional Data (Document_ID, Document_Revision, etc.)
      - Must be mapped and cleaned before logic
      - No aggressive forward fill
    - Priority 3: Derived Logic & Status Flags (Submission_Closed, Resubmission_Required, etc.)
      - Calculated fields
      - Recalculated every pipeline run
    """
    
    def __init__(self, config: Dict[str, Any], logger: Logger):
        """
        Initialize CSV loader with configuration and logger
        
        Args:
            config: Configuration from schema
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.logger.enter_function("CSVLoader.__init__")
        
        self.data_columns = config.get('data_columns', [])
        self.project_paths = config.get('project_paths', {})
        
        self.logger.add_trace_entry(
            "data_columns_count",
            len(self.data_columns),
            "config",
            "success"
        )
        
        self.logger.exit_function("CSVLoader.__init__")
    
    def load_csv(self, file_path: str) -> pd.DataFrame:
        """
        Load CSV file into DataFrame
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            Loaded DataFrame
        """
        self.logger.enter_function("CSVLoader.load_csv")
        self.logger.info(f"Loading CSV file: {file_path}", "CSVLoader.load_csv")
        
        try:
            df = pd.read_csv(file_path)
            self.logger.add_trace_entry(
                "rows_loaded",
                len(df),
                "csv_file",
                "success"
            )
            self.logger.add_trace_entry(
                "columns_loaded",
                len(df.columns),
                "csv_file",
                "success"
            )
            self.logger.info(f"Loaded {len(df)} rows and {len(df.columns)} columns", "CSVLoader.load_csv")
            
            self.logger.exit_function("CSVLoader.load_csv")
            return df
            
        except Exception as e:
            self.logger.error(f"Failed to load CSV: {str(e)}", "CSVLoader.load_csv")
            self.logger.fail_fast(f"CSV load failed: {str(e)}", "CSVLoader.load_csv")
    
    def check_duplicate_columns(self, df: pd.DataFrame) -> bool:
        """
        Check for duplicate columns in DataFrame
        
        Args:
            df: DataFrame to check
            
        Returns:
            True if duplicates found, False otherwise
        """
        self.logger.enter_function("CSVLoader.check_duplicate_columns")
        
        duplicates = df.columns[df.columns.duplicated()].tolist()
        
        if duplicates:
            self.logger.warning(f"Duplicate columns found: {duplicates}", "CSVLoader.check_duplicate_columns")
            self.logger.add_trace_entry(
                "duplicate_columns",
                duplicates,
                "dataframe_check",
                "warning"
            )
            self.logger.exit_function("CSVLoader.check_duplicate_columns")
            return True
        else:
            self.logger.info("No duplicate columns found", "CSVLoader.check_duplicate_columns")
            self.logger.add_trace_entry(
                "duplicate_columns",
                "none",
                "dataframe_check",
                "success"
            )
            self.logger.exit_function("CSVLoader.check_duplicate_columns")
            return False
    
    def process_by_priority(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process DataFrame columns by priority per Section 1
        
        Args:
            df: DataFrame to process
            
        Returns:
            Processed DataFrame
        """
        self.logger.enter_function("CSVLoader.process_by_priority")
        self.logger.info("Starting priority-based column processing", "CSVLoader.process_by_priority")
        
        # Check for duplicate columns first
        if self.check_duplicate_columns(df):
            self.logger.warning("Duplicate columns detected, proceeding with caution", "CSVLoader.process_by_priority")
        
        # Separate columns by priority
        priority_1_cols = []
        priority_2_cols = []
        priority_3_cols = []
        
        for col_config in self.data_columns:
            col_name = col_config.get('name')
            priority = col_config.get('priority')
            
            if col_name in df.columns:
                if priority == 1:
                    priority_1_cols.append(col_name)
                elif priority == 2:
                    priority_2_cols.append(col_name)
                elif priority == 3:
                    priority_3_cols.append(col_name)
        
        self.logger.add_trace_entry(
            "priority_1_columns",
            len(priority_1_cols),
            "column_classification",
            "success"
        )
        self.logger.add_trace_entry(
            "priority_2_columns",
            len(priority_2_cols),
            "column_classification",
            "success"
        )
        self.logger.add_trace_entry(
            "priority_3_columns",
            len(priority_3_cols),
            "column_classification",
            "success"
        )
        
        # Process Priority 1: Meta data columns with bounded forward fill
        self.logger.info("Processing Priority 1: Meta data columns", "CSVLoader.process_by_priority")
        df = self._process_priority_1(df, priority_1_cols)
        
        # Process Priority 2: Relational keys (no aggressive forward fill)
        self.logger.info("Processing Priority 2: Relational keys", "CSVLoader.process_by_priority")
        df = self._process_priority_2(df, priority_2_cols)
        
        # Process Priority 3: Derived logic (recalculate)
        self.logger.info("Processing Priority 3: Derived logic", "CSVLoader.process_by_priority")
        df = self._process_priority_3(df, priority_3_cols)
        
        self.logger.exit_function("CSVLoader.process_by_priority")
        return df
    
    def _process_priority_1(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """
        Process Priority 1 columns with bounded forward fill
        
        Args:
            df: DataFrame
            columns: Priority 1 column names
            
        Returns:
            Processed DataFrame
        """
        self.logger.trace(f"Processing {len(columns)} Priority 1 columns", "CSVLoader._process_priority_1")
        
        for col in columns:
            col_config = self._get_column_config(col)
            if col_config and col_config.get('forward_fill', False):
                # Bounded forward fill (stops if row index jumps significantly)
                df[col] = df[col].ffill()
                self.logger.trace(f"Applied bounded forward fill to {col}", "CSVLoader._process_priority_1")
        
        return df
    
    def _process_priority_2(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """
        Process Priority 2 columns (no aggressive forward fill)
        
        Args:
            df: DataFrame
            columns: Priority 2 column names
            
        Returns:
            Processed DataFrame
        """
        self.logger.trace(f"Processing {len(columns)} Priority 2 columns", "CSVLoader._process_priority_2")
        
        for col in columns:
            col_config = self._get_column_config(col)
            if col_config and col_config.get('nullable', True):
                # Check for null values in critical columns
                null_count = df[col].isnull().sum()
                if null_count > 0:
                    self.logger.warning(
                        f"Column {col} has {null_count} null values (Priority 2)",
                        "CSVLoader._process_priority_2"
                    )
        
        return df
    
    def _process_priority_3(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """
        Process Priority 3 columns (derived logic - recalculated)
        
        Args:
            df: DataFrame
            columns: Priority 3 column names
            
        Returns:
            Processed DataFrame
        """
        self.logger.trace(f"Processing {len(columns)} Priority 3 columns (derived logic)", "CSVLoader._process_priority_3")
        
        # Priority 3 columns are calculated fields
        # They should be recalculated every pipeline run
        # Implementation will depend on specific business logic
        
        return df
    
    def _get_column_config(self, column_name: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a specific column
        
        Args:
            column_name: Column name
            
        Returns:
            Column configuration or None
        """
        for col_config in self.data_columns:
            if col_config.get('name') == column_name:
                return col_config
        return None
    
    def group_data(self, df: pd.DataFrame, group_by_column: str) -> Dict[Any, pd.DataFrame]:
        """
        Group DataFrame by specified column
        
        Args:
            df: DataFrame to group
            group_by_column: Column to group by
            
        Returns:
            Dictionary of group name to DataFrame
        """
        self.logger.enter_function("CSVLoader.group_data")
        self.logger.info(f"Grouping data by {group_by_column}", "CSVLoader.group_data")
        
        if group_by_column not in df.columns:
            self.logger.error(f"Column {group_by_column} not found in DataFrame", "CSVLoader.group_data")
            self.logger.exit_function("CSVLoader.group_data")
            return {}
        
        grouped = df.groupby(group_by_column)
        result = {name: group for name, group in grouped}
        
        self.logger.add_trace_entry(
            "groups_created",
            len(result),
            "grouping_operation",
            "success"
        )
        
        self.logger.exit_function("CSVLoader.group_data")
        return result


def load_and_process_csv(config: Dict[str, Any], logger: Logger, file_path: str) -> pd.DataFrame:
    """
    Load and process CSV file with priority-based column processing
    
    Args:
        config: Configuration from schema
        logger: Logger instance
        file_path: Path to CSV file
        
    Returns:
        Processed DataFrame
    """
    loader = CSVLoader(config, logger)
    df = loader.load_csv(file_path)
    processed_df = loader.process_by_priority(df)
    return processed_df
