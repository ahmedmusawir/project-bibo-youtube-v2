"""
Simple logging utility for Bibo Video Generator.
Logs to both console and file with timestamps.
"""

import os
import sys
from datetime import datetime
from pathlib import Path


class Logger:
    """Simple logger that writes to both console and file."""
    
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        self.log_file = None
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
        
    def start(self, project_name=None):
        """Start logging to a new log file."""
        os.makedirs(self.log_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if project_name:
            filename = f"{timestamp}_{project_name}.log"
        else:
            filename = f"{timestamp}.log"
        
        log_path = os.path.join(self.log_dir, filename)
        self.log_file = open(log_path, "w", encoding="utf-8")
        
        # Write header
        self._write_to_file(f"=== Bibo Video Generator Log ===")
        self._write_to_file(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        if project_name:
            self._write_to_file(f"Project: {project_name}")
        self._write_to_file("=" * 40 + "\n")
        
        return log_path
    
    def _write_to_file(self, message):
        """Write message to log file with timestamp."""
        if self.log_file:
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.log_file.write(f"[{timestamp}] {message}\n")
            self.log_file.flush()
    
    def log(self, message):
        """Log message to both console and file."""
        print(message)
        self._write_to_file(message)
    
    def stop(self):
        """Stop logging and close file."""
        if self.log_file:
            self._write_to_file("\n" + "=" * 40)
            self._write_to_file(f"Ended: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            self.log_file.close()
            self.log_file = None


class TeeOutput:
    """Tee stdout/stderr to both console and log file."""
    
    def __init__(self, original, log_file):
        self.original = original
        self.log_file = log_file
    
    def write(self, message):
        self.original.write(message)
        if self.log_file and message.strip():
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.log_file.write(f"[{timestamp}] {message}")
            if not message.endswith("\n"):
                self.log_file.write("\n")
            self.log_file.flush()
    
    def flush(self):
        self.original.flush()
        if self.log_file:
            self.log_file.flush()


# Global logger instance
_logger = None


def init_logging(project_name=None, log_dir="logs"):
    """Initialize logging for the session."""
    global _logger
    _logger = Logger(log_dir)
    log_path = _logger.start(project_name)
    
    # Redirect stdout and stderr to tee
    sys.stdout = TeeOutput(sys.__stdout__, _logger.log_file)
    sys.stderr = TeeOutput(sys.__stderr__, _logger.log_file)
    
    return log_path


def stop_logging():
    """Stop logging and restore stdout/stderr."""
    global _logger
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
    if _logger:
        _logger.stop()
        _logger = None


def get_log_path():
    """Get current log file path."""
    global _logger
    if _logger and _logger.log_file:
        return _logger.log_file.name
    return None
