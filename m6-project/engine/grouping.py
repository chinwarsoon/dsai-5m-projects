"""
Chunk Grouping Strategies for Document Submittal Register
Implements 4 grouping strategies for testing and optimization
"""

import pandas as pd
from typing import Dict, Any, List, Optional, Callable
from .logger import Logger


class GroupingStrategy:
    """Base class for grouping strategies"""
    
    def __init__(self, name: str, column: str, logger: Logger):
        """
        Initialize grouping strategy
        
        Args:
            name: Strategy name
            column: Column to group by
            logger: Logger instance
        """
        self.name = name
        self.column = column
        self.logger = logger
        self.logger.enter_function(f"GroupingStrategy.__init__.{name}")
        self.logger.exit_function(f"GroupingStrategy.__init__.{name}")
    
    def group(self, df: pd.DataFrame) -> Dict[Any, pd.DataFrame]:
        """
        Group DataFrame by strategy column
        
        Args:
            df: DataFrame to group
            
        Returns:
            Dictionary of group key to DataFrame
        """
        self.logger.enter_function(f"GroupingStrategy.group.{self.name}")
        self.logger.info(f"Grouping by {self.column} using {self.name} strategy", f"GroupingStrategy.group.{self.name}")
        
        if self.column not in df.columns:
            self.logger.error(f"Column {self.column} not found in DataFrame", f"GroupingStrategy.group.{self.name}")
            self.logger.exit_function(f"GroupingStrategy.group.{self.name}")
            return {}
        
        grouped = df.groupby(self.column)
        result = {key: group for key, group in grouped}
        
        self.logger.add_trace_entry(
            f"{self.name}_groups_count",
            len(result),
            "grouping_operation",
            "success"
        )
        
        self.logger.info(f"Created {len(result)} groups using {self.name} strategy", f"GroupingStrategy.group.{self.name}")
        self.logger.exit_function(f"GroupingStrategy.group.{self.name}")
        return result


class SubmissionSessionGrouping(GroupingStrategy):
    """Group by Submission_Session"""
    
    def __init__(self, logger: Logger):
        super().__init__("submission_session", "Submission_Session", logger)


class DocumentIDGrouping(GroupingStrategy):
    """Group by Document_ID"""
    
    def __init__(self, logger: Logger):
        super().__init__("document_id", "Document_ID", logger)


class ValidationErrorGrouping(GroupingStrategy):
    """Group by Validation_Errors"""
    
    def __init__(self, logger: Logger):
        super().__init__("validation_error", "Validation_Errors", logger)
    
    def group(self, df: pd.DataFrame) -> Dict[Any, pd.DataFrame]:
        """
        Group by validation errors with special handling for null values
        
        Args:
            df: DataFrame to group
            
        Returns:
            Dictionary of group key to DataFrame
        """
        self.logger.enter_function("ValidationErrorGrouping.group")
        self.logger.info("Grouping by Validation_Errors with null handling", "ValidationErrorGrouping.group")
        
        if self.column not in df.columns:
            self.logger.error(f"Column {self.column} not found in DataFrame", "ValidationErrorGrouping.group")
            self.logger.exit_function("ValidationErrorGrouping.group")
            return {}
        
        # Fill null values with "NO_ERRORS" for grouping
        df_copy = df.copy()
        df_copy[self.column] = df_copy[self.column].fillna("NO_ERRORS")
        
        grouped = df_copy.groupby(self.column)
        result = {key: group for key, group in grouped}
        
        self.logger.add_trace_entry(
            "validation_error_groups",
            len(result),
            "grouping_operation",
            "success"
        )
        
        self.logger.exit_function("ValidationErrorGrouping.group")
        return result


class DepartmentGrouping(GroupingStrategy):
    """Group by Department"""
    
    def __init__(self, logger: Logger):
        super().__init__("department", "Department", logger)


class GroupingManager:
    """
    Manager for all grouping strategies
    Allows selection and comparison of different strategies
    """
    
    def __init__(self, config: Dict[str, Any], logger: Logger):
        """
        Initialize grouping manager
        
        Args:
            config: Configuration from schema
            logger: Logger instance
        """
        self.logger = logger
        self.logger.enter_function("GroupingManager.__init__")
        
        self.strategies = {}
        self.config = config
        self.grouping_config = config.get('grouping_strategies', [])
        
        # Initialize all strategies
        for strategy_config in self.grouping_config:
            name = strategy_config.get('name')
            enabled = strategy_config.get('enabled', False)
            
            if enabled:
                self.strategies[name] = self._create_strategy(name)
                self.logger.info(f"Initialized strategy: {name}", "GroupingManager.__init__")
        
        self.logger.add_trace_entry(
            "enabled_strategies",
            list(self.strategies.keys()),
            "strategy_initialization",
            "success"
        )
        
        self.logger.exit_function("GroupingManager.__init__")
    
    def _create_strategy(self, name: str) -> GroupingStrategy:
        """
        Create strategy instance by name
        
        Args:
            name: Strategy name
            
        Returns:
            Strategy instance
        """
        if name == "submission_session":
            return SubmissionSessionGrouping(self.logger)
        elif name == "document_id":
            return DocumentIDGrouping(self.logger)
        elif name == "validation_error":
            return ValidationErrorGrouping(self.logger)
        elif name == "department":
            return DepartmentGrouping(self.logger)
        else:
            self.logger.warning(f"Unknown strategy: {name}", "GroupingManager._create_strategy")
            return None
    
    def get_strategy(self, name: str) -> Optional[GroupingStrategy]:
        """
        Get strategy by name
        
        Args:
            name: Strategy name
            
        Returns:
            Strategy instance or None
        """
        return self.strategies.get(name)
    
    def group_with_strategy(self, df: pd.DataFrame, strategy_name: str) -> Dict[Any, pd.DataFrame]:
        """
        Group DataFrame using specified strategy
        
        Args:
            df: DataFrame to group
            strategy_name: Name of strategy to use
            
        Returns:
            Dictionary of group key to DataFrame
        """
        self.logger.enter_function("GroupingManager.group_with_strategy")
        
        strategy = self.get_strategy(strategy_name)
        if not strategy:
            self.logger.error(f"Strategy {strategy_name} not found or not enabled", "GroupingManager.group_with_strategy")
            self.logger.exit_function("GroupingManager.group_with_strategy")
            return {}
        
        result = strategy.group(df)
        self.logger.exit_function("GroupingManager.group_with_strategy")
        return result
    
    def group_with_all_strategies(self, df: pd.DataFrame) -> Dict[str, Dict[Any, pd.DataFrame]]:
        """
        Group DataFrame using all enabled strategies
        
        Args:
            df: DataFrame to group
            
        Returns:
            Dictionary of strategy name to grouped results
        """
        self.logger.enter_function("GroupingManager.group_with_all_strategies")
        self.logger.info(f"Grouping with all {len(self.strategies)} strategies", "GroupingManager.group_with_all_strategies")
        
        results = {}
        for name, strategy in self.strategies.items():
            results[name] = strategy.group(df)
        
        self.logger.exit_function("GroupingManager.group_with_all_strategies")
        return results
    
    def compare_strategies(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Compare grouping strategies and return metrics
        
        Args:
            df: DataFrame to compare on
            
        Returns:
            Comparison metrics
        """
        self.logger.enter_function("GroupingManager.compare_strategies")
        
        comparison = {}
        for name, strategy in self.strategies.items():
            groups = strategy.group(df)
            comparison[name] = {
                "group_count": len(groups),
                "avg_group_size": sum(len(g) for g in groups.values()) / len(groups) if groups else 0,
                "max_group_size": max(len(g) for g in groups.values()) if groups else 0,
                "min_group_size": min(len(g) for g in groups.values()) if groups else 0
            }
        
        self.logger.add_debug_info("strategy_comparison", comparison)
        self.logger.exit_function("GroupingManager.compare_strategies")
        return comparison


def get_grouping_manager(config: Dict[str, Any], logger: Logger) -> GroupingManager:
    """
    Get grouping manager instance
    
    Args:
        config: Configuration from schema
        logger: Logger instance
        
    Returns:
        GroupingManager instance
    """
    return GroupingManager(config, logger)
