#!/usr/bin/env python3
"""
Logger setup untuk MX Tweaks Pro
"""

import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler

def setup_logger(debug=False):
    """Setup logger dengan konfigurasi yang tepat"""
    
    # Buat direktori log
    log_dir = Path.home() / '.config' / 'mx-tweaks-pro' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Setup logger
    logger = logging.getLogger('mx-tweaks-pro')
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # File handler dengan rotation
    file_handler = RotatingFileHandler(
        log_dir / 'mx-tweaks-pro.log',
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG if debug else logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    if debug:
        logger.addHandler(console_handler)
    
    return logger