import logging
import sys
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

@dataclass
class LogConfig:
    level: int = logging.INFO
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"
    file_path: Optional[str] = None
    max_bytes: int = 10 * 1024 * 1024
    backup_count: int = 5
    console_output: bool = True

class LoggingPolicy:
    
    def __init__(self, config: LogConfig):
        self.config = config
        self._setup_logging()
    
    def _setup_logging(self):
        root_logger = logging.getLogger()
        root_logger.setLevel(self.config.level)
        
        root_logger.handlers.clear()
        
        formatter = logging.Formatter(
            fmt=self.config.format,
            datefmt=self.config.date_format
        )
        
        if self.config.file_path:
            log_path = Path(self.config.file_path)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = RotatingFileHandler(
                filename=str(log_path),
                maxBytes=self.config.max_bytes,
                backupCount=self.config.backup_count
            )
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        
        if self.config.console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)
    
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        return logging.getLogger(name)
    
    def update_level(self, level: int):
        self.config.level = level
        logging.getLogger().setLevel(level)

def setup_module_logger(module_name: str, level: Optional[int] = None) -> logging.Logger:
    logger = logging.getLogger(module_name)
    if level is not None:
        logger.setLevel(level)
    return logger
