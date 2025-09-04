#!/usr/bin/env python3
"""
Config Manager untuk MX Tweaks Pro
Mengelola konfigurasi aplikasi
"""

import os
import json
from pathlib import Path
from configparser import ConfigParser

class ConfigManager:
    def __init__(self):
        self.config_dir = Path.home() / '.config' / 'mx-tweaks-pro'
        self.config_file = self.config_dir / 'config.ini'
        self.backup_dir = self.config_dir / 'backups'
        
        # Buat direktori config jika belum ada
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Load atau buat config default
        self.config = ConfigParser()
        self.load_config()
    
    def load_config(self):
        """Load konfigurasi dari file"""
        if self.config_file.exists():
            self.config.read(self.config_file)
        else:
            self.create_default_config()
    
    def create_default_config(self):
        """Buat konfigurasi default"""
        self.config['general'] = {
            'auto_backup': 'true',
            'confirm_dangerous': 'true',
            'log_level': 'INFO',
            'theme': 'auto'
        }
        
        self.config['tweaks'] = {
            'auto_clean_temp': 'false',
            'auto_update_cache': 'true',
            'performance_mode': 'balanced'
        }
        
        self.config['backup'] = {
            'max_backups': '10',
            'backup_before_tweak': 'true'
        }
        
        self.save_config()
    
    def save_config(self):
        """Simpan konfigurasi ke file"""
        with open(self.config_file, 'w') as f:
            self.config.write(f)
    
    def get(self, section, key, fallback=None):
        """Ambil nilai konfigurasi"""
        return self.config.get(section, key, fallback=fallback)
    
    def getboolean(self, section, key, fallback=False):
        """Ambil nilai boolean dari konfigurasi"""
        return self.config.getboolean(section, key, fallback=fallback)
    
    def getint(self, section, key, fallback=0):
        """Ambil nilai integer dari konfigurasi"""
        return self.config.getint(section, key, fallback=fallback)
    
    def set(self, section, key, value):
        """Set nilai konfigurasi"""
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, str(value))
        self.save_config()