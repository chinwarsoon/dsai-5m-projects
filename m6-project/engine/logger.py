"""
Tiered Logging System for M6 Project
Implements Section 6 of agent_rule.md: Debug and logging
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum


class LogLevel(Enum):
    """Logging levels per Section 6"""
    SILENT = 0  # Only errors
    INFO = 1    # Status/info - milestone progress / high-level workflow status
    WARNING = 2  # Warning/debug - warnings / detailed information for debugging
    TRACE = 3   # Deep technical info - OS specific paths, JSON raw extraction, etc.


class Logger:
    """
    Tiered logging system implementation
    - Categorized logging for different severity levels
    - Debug object collection for single results dictionary
    - Structured trace table for parameter flow
    - Indented print messages per hierarchy level
    - Function name and calling context in messages
    - Global parameter state tracking
    - Fail-fast metadata for critical errors
    - System snapshot for level 1 logging
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize logger with configuration
        
        Args:
            config: Logging configuration from schema
        """
        self.level = LogLevel(config.get('level', 2))
        self.log_to_file = config.get('log_to_file', True)
        self.log_file_path = config.get('log_file_path', 'log/application.log')
        self.include_timestamp = config.get('include_timestamp', True)
        self.include_function_name = config.get('include_function_name', True)
        
        self.debug_info: Dict[str, Any] = {}
        self.trace_table: list = []
        self.depth = 0
        self.function_stack = []
        
        # Ensure log directory exists
        if self.log_to_file:
            os.makedirs(os.path.dirname(self.log_file_path), exist_ok=True)
    
    def _format_message(self, level: LogLevel, message: str, function_name: Optional[str] = None) -> str:
        """
        Format log message with timestamp, level, and function name
        
        Args:
            level: Log level
            message: Log message
            function_name: Optional function name
            
        Returns:
            Formatted message string
        """
        parts = []
        
        if self.include_timestamp:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            parts.append(f"[{timestamp}]")
        
        parts.append(f"[{level.name}]")
        
        if self.include_function_name and function_name:
            parts.append(f"[{function_name}]")
        
        # Add indentation based on depth
        indent = "  " * self.depth
        parts.append(indent)
        
        parts.append(message)
        
        return " ".join(parts)
    
    def log(self, level: LogLevel, message: str, function_name: Optional[str] = None):
        """
        Log message at specified level
        
        Args:
            level: Log level
            message: Log message
            function_name: Optional function name
        """
        if level.value <= self.level.value:
            formatted_message = self._format_message(level, message, function_name)
            print(formatted_message)
            
            if self.log_to_file:
                with open(self.log_file_path, 'a') as f:
                    f.write(formatted_message + '\n')
    
    def info(self, message: str, function_name: Optional[str] = None):
        """Log info message (level 1)"""
        self.log(LogLevel.INFO, message, function_name)
    
    def warning(self, message: str, function_name: Optional[str] = None):
        """Log warning message (level 2)"""
        self.log(LogLevel.WARNING, message, function_name)
    
    def trace(self, message: str, function_name: Optional[str] = None):
        """Log trace message (level 3)"""
        self.log(LogLevel.TRACE, message, function_name)
    
    def error(self, message: str, function_name: Optional[str] = None):
        """Log error message (always logged)"""
        self.log(LogLevel.SILENT, f"ERROR: {message}", function_name)
    
    def add_debug_info(self, key: str, value: Any):
        """
        Add debug information to debug object
        
        Args:
            key: Debug info key
            value: Debug info value
        """
        self.debug_info[key] = value
    
    def add_trace_entry(self, parameter: str, value: Any, source: str, status: str = "success"):
        """
        Add entry to trace table
        
        Args:
            parameter: Parameter name
            value: Parameter value
            source: Source of parameter
            status: Status of parameter resolution
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "parameter": parameter,
            "value": str(value),
            "source": source,
            "status": status,
            "depth": self.depth
        }
        self.trace_table.append(entry)
    
    def enter_function(self, function_name: str):
        """
        Enter function - increment depth and add to stack
        
        Args:
            function_name: Function name
        """
        self.function_stack.append(function_name)
        self.depth += 1
        self.trace(f"Entering function: {function_name}", function_name)
    
    def exit_function(self, function_name: str):
        """
        Exit function - decrement depth and remove from stack
        
        Args:
            function_name: Function name
        """
        self.trace(f"Exiting function: {function_name}", function_name)
        self.depth -= 1
        if self.function_stack and self.function_stack[-1] == function_name:
            self.function_stack.pop()
    
    def get_current_function(self) -> Optional[str]:
        """Get current function name from stack"""
        return self.function_stack[-1] if self.function_stack else None
    
    def save_debug_log(self, file_path: str):
        """
        Save debug information to JSON file
        
        Args:
            file_path: Path to save debug log
        """
        debug_data = {
            "debug_info": self.debug_info,
            "trace_table": self.trace_table,
            "timestamp": datetime.now().isoformat()
        }
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump(debug_data, f, indent=2)
        
        self.info(f"Debug log saved to {file_path}", "save_debug_log")
    
    def take_system_snapshot(self) -> Dict[str, Any]:
        """
        Take system snapshot for level 1 logging
        
        Returns:
            System snapshot dictionary
        """
        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "python_version": os.sys.version,
            "working_directory": os.getcwd(),
            "environment_variables": dict(os.environ)
        }
        self.add_debug_info("system_snapshot", snapshot)
        return snapshot
    
    def fail_fast(self, message: str, function_name: Optional[str] = None):
        """
        Fail-fast on critical errors
        
        Args:
            message: Error message
            function_name: Optional function name
        """
        self.error(f"CRITICAL ERROR - Stopping execution: {message}", function_name)
        raise RuntimeError(message)


def get_logger(config: Optional[Dict[str, Any]] = None) -> Logger:
    """
    Get logger instance with configuration
    
    Args:
        config: Optional logging configuration
        
    Returns:
        Logger instance
    """
    if config is None:
        config = {
            'level': 2,
            'log_to_file': True,
            'log_file_path': 'log/application.log',
            'include_timestamp': True,
            'include_function_name': True
        }
    return Logger(config)
