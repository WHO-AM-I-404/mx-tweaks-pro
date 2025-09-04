#!/usr/bin/env python3
"""
Backup Manager untuk MX Tweaks Pro
Mengelola backup dan restore konfigurasi sistem
"""

import os
import shutil
import json
import datetime
from pathlib import Path

class BackupManager:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.backup_dir = Path.home() / '.config' / 'mx-tweaks-pro' / 'backups'
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self, name, files_to_backup):
        """Buat backup dari file-file yang ditentukan"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{name}_{timestamp}"
        backup_path = self.backup_dir / backup_name
        backup_path.mkdir(exist_ok=True)
        
        backed_up_files = []
        
        for file_path in files_to_backup:
            if os.path.exists(file_path):
                try:
                    dest_path = backup_path / Path(file_path).name
                    shutil.copy2(file_path, dest_path)
                    backed_up_files.append(file_path)
                    self.logger.info(f"Backup: {file_path} -> {dest_path}")
                except Exception as e:
                    self.logger.error(f"Gagal backup {file_path}: {e}")
        
        # Simpan metadata backup
        metadata = {
            'name': name,
            'timestamp': timestamp,
            'files': backed_up_files,
            'created_at': datetime.datetime.now().isoformat()
        }
        
        with open(backup_path / 'metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return backup_name
    
    def list_backups(self):
        """List semua backup yang tersedia"""
        backups = []
        
        for backup_dir in self.backup_dir.iterdir():
            if backup_dir.is_dir():
                metadata_file = backup_dir / 'metadata.json'
                if metadata_file.exists():
                    try:
                        with open(metadata_file, 'r') as f:
                            metadata = json.load(f)
                        backups.append({
                            'path': backup_dir,
                            'metadata': metadata
                        })
                    except Exception as e:
                        self.logger.error(f"Error reading metadata for {backup_dir}: {e}")
        
        return sorted(backups, key=lambda x: x['metadata']['created_at'], reverse=True)
    
    def restore_backup(self, backup_name):
        """Restore backup yang dipilih"""
        backup_path = self.backup_dir / backup_name
        
        if not backup_path.exists():
            self.logger.error(f"Backup {backup_name} tidak ditemukan")
            return False
        
        metadata_file = backup_path / 'metadata.json'
        if not metadata_file.exists():
            self.logger.error(f"Metadata backup {backup_name} tidak ditemukan")
            return False
        
        try:
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            restored_files = []
            for original_file in metadata['files']:
                backup_file = backup_path / Path(original_file).name
                if backup_file.exists():
                    try:
                        shutil.copy2(backup_file, original_file)
                        restored_files.append(original_file)
                        self.logger.info(f"Restored: {backup_file} -> {original_file}")
                    except Exception as e:
                        self.logger.error(f"Gagal restore {original_file}: {e}")
            
            return len(restored_files) > 0
            
        except Exception as e:
            self.logger.error(f"Error restoring backup {backup_name}: {e}")
            return False
    
    def cleanup_old_backups(self, max_backups=None):
        """Hapus backup lama untuk menghemat space"""
        if max_backups is None:
            max_backups = self.config.getint('backup', 'max_backups', fallback=10)
        
        backups = self.list_backups()
        
        if len(backups) > max_backups:
            backups_to_delete = backups[max_backups:]
            
            for backup in backups_to_delete:
                try:
                    shutil.rmtree(backup['path'])
                    self.logger.info(f"Deleted old backup: {backup['path']}")
                except Exception as e:
                    self.logger.error(f"Error deleting backup {backup['path']}: {e}")