#!/usr/bin/env python3
"""
Automated Backup Scheduler for MX Tweaks Pro v2.1
Advanced backup scheduling and management system
"""

import os
import subprocess
import time
import shutil
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.prompt import Confirm, Prompt, IntPrompt
from rich.panel import Panel
from rich.table import Table
from rich import box
import schedule
import threading

class BackupScheduler:
    """Advanced backup scheduling and management system"""
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.console = Console()
        
        # Backup configuration
        self.backup_dir = Path.home() / '.mx-tweaks-pro' / 'backups'
        self.config_dir = Path.home() / '.mx-tweaks-pro' / 'scheduler'
        self.schedule_file = self.config_dir / 'schedule.json'
        
        # Create directories
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Scheduler state
        self.scheduler_running = False
        self.scheduler_thread = None
        
        # Load existing schedules
        self.schedules = self._load_schedules()
    
    def _load_schedules(self) -> Dict:
        """Load backup schedules from configuration"""
        try:
            if self.schedule_file.exists():
                with open(self.schedule_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            self.logger.error(f"Error loading schedules: {e}")
            return {}
    
    def _save_schedules(self):
        """Save backup schedules to configuration"""
        try:
            with open(self.schedule_file, 'w') as f:
                json.dump(self.schedules, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving schedules: {e}")
    
    def create_backup(self, backup_name: Optional[str] = None, 
                     include_config: bool = True,
                     include_home: bool = False,
                     include_system: bool = False,
                     custom_paths: List[str] = None) -> Dict:
        """Create a comprehensive system backup"""
        if backup_name is None:
            backup_name = f"mx-tweaks-backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        backup_path = self.backup_dir / backup_name
        backup_path.mkdir(exist_ok=True)
        
        self.console.print(Panel(
            f"[bold cyan]Creating Backup: {backup_name}[/bold cyan]\n"
            f"Location: {backup_path}\n"
            f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            title="🔄 Backup Process",
            border_style="bright_blue"
        ))
        
        backup_info = {
            "name": backup_name,
            "timestamp": time.time(),
            "path": str(backup_path),
            "components": [],
            "size": 0,
            "files_count": 0,
            "success": True,
            "errors": []
        }
        
        total_tasks = sum([
            1 if include_config else 0,
            1 if include_home else 0,
            1 if include_system else 0,
            len(custom_paths) if custom_paths else 0
        ])
        
        current_task = 0
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=self.console
        ) as progress:
            main_task = progress.add_task("Creating backup...", total=total_tasks)
            
            # Backup system configuration
            if include_config:
                current_task += 1
                progress.update(main_task, description=f"Backing up system configuration ({current_task}/{total_tasks})")
                
                config_backup = self._backup_system_configuration(backup_path)
                backup_info["components"].append(config_backup)
                
                if not config_backup["success"]:
                    backup_info["errors"].extend(config_backup["errors"])
                
                progress.advance(main_task)
            
            # Backup home directory (selective)
            if include_home:
                current_task += 1
                progress.update(main_task, description=f"Backing up home directory ({current_task}/{total_tasks})")
                
                home_backup = self._backup_home_directory(backup_path)
                backup_info["components"].append(home_backup)
                
                if not home_backup["success"]:
                    backup_info["errors"].extend(home_backup["errors"])
                
                progress.advance(main_task)
            
            # Backup system files
            if include_system:
                current_task += 1
                progress.update(main_task, description=f"Backing up system files ({current_task}/{total_tasks})")
                
                system_backup = self._backup_system_files(backup_path)
                backup_info["components"].append(system_backup)
                
                if not system_backup["success"]:
                    backup_info["errors"].extend(system_backup["errors"])
                
                progress.advance(main_task)
            
            # Backup custom paths
            if custom_paths:
                for custom_path in custom_paths:
                    current_task += 1
                    progress.update(main_task, description=f"Backing up {custom_path} ({current_task}/{total_tasks})")
                    
                    custom_backup = self._backup_custom_path(backup_path, custom_path)
                    backup_info["components"].append(custom_backup)
                    
                    if not custom_backup["success"]:
                        backup_info["errors"].extend(custom_backup["errors"])
                    
                    progress.advance(main_task)
        
        # Calculate total backup size and file count
        backup_info["size"] = self._calculate_directory_size(backup_path)
        backup_info["files_count"] = sum(len(list(Path(backup_path).rglob('*'))) for _ in [None])
        
        # Save backup metadata
        metadata_file = backup_path / 'backup_info.json'
        with open(metadata_file, 'w') as f:
            json.dump(backup_info, f, indent=2)
        
        # Create backup summary
        self._display_backup_summary(backup_info)
        
        self.logger.info(f"Backup created: {backup_name} at {backup_path}")
        return backup_info
    
    def _backup_system_configuration(self, backup_path: Path) -> Dict:
        """Backup system configuration files"""
        config_backup_path = backup_path / 'system_config'
        config_backup_path.mkdir(exist_ok=True)
        
        config_files = [
            '/etc/fstab',
            '/etc/hosts',
            '/etc/hostname',
            '/etc/resolv.conf',
            '/etc/network/interfaces',
            '/etc/ssh/sshd_config',
            '/etc/apt/sources.list',
            '/etc/crontab',
            '/etc/sudoers'
        ]
        
        config_dirs = [
            '/etc/apt/sources.list.d',
            '/etc/NetworkManager',
            '/etc/systemd/system',
            '/etc/ufw'
        ]
        
        result = {
            "component": "system_configuration",
            "success": True,
            "files_backed_up": 0,
            "errors": [],
            "size": 0
        }
        
        # Backup individual config files
        for config_file in config_files:
            try:
                if os.path.exists(config_file):
                    dest_file = config_backup_path / Path(config_file).name
                    shutil.copy2(config_file, dest_file)
                    result["files_backed_up"] += 1
            except Exception as e:
                result["errors"].append(f"Failed to backup {config_file}: {e}")
                result["success"] = False
        
        # Backup config directories
        for config_dir in config_dirs:
            try:
                if os.path.exists(config_dir):
                    dest_dir = config_backup_path / Path(config_dir).name
                    shutil.copytree(config_dir, dest_dir, ignore_errors=True)
                    result["files_backed_up"] += len(list(dest_dir.rglob('*')))
            except Exception as e:
                result["errors"].append(f"Failed to backup {config_dir}: {e}")
        
        # Backup installed packages list
        try:
            packages_file = config_backup_path / 'installed_packages.txt'
            subprocess.run(['dpkg', '--get-selections'], 
                         stdout=open(packages_file, 'w'), check=True)
            result["files_backed_up"] += 1
        except Exception as e:
            result["errors"].append(f"Failed to backup package list: {e}")
        
        result["size"] = self._calculate_directory_size(config_backup_path)
        return result
    
    def _backup_home_directory(self, backup_path: Path) -> Dict:
        """Backup selective home directory contents"""
        home_backup_path = backup_path / 'home'
        home_backup_path.mkdir(exist_ok=True)
        home_dir = Path.home()
        
        # Important directories to backup from home
        important_dirs = [
            '.config',
            '.local/share',
            '.ssh',
            '.gnupg',
            'Documents',
            'Desktop',
            'Pictures',
            'Downloads'
        ]
        
        # Important files to backup
        important_files = [
            '.bashrc',
            '.bash_profile',
            '.profile',
            '.vimrc',
            '.gitconfig'
        ]
        
        result = {
            "component": "home_directory",
            "success": True,
            "files_backed_up": 0,
            "errors": [],
            "size": 0
        }
        
        # Backup important directories
        for dir_name in important_dirs:
            src_dir = home_dir / dir_name
            if src_dir.exists():
                try:
                    dest_dir = home_backup_path / dir_name
                    shutil.copytree(src_dir, dest_dir, ignore_errors=True)
                    result["files_backed_up"] += len(list(dest_dir.rglob('*')))
                except Exception as e:
                    result["errors"].append(f"Failed to backup {dir_name}: {e}")
                    result["success"] = False
        
        # Backup important files
        for file_name in important_files:
            src_file = home_dir / file_name
            if src_file.exists():
                try:
                    dest_file = home_backup_path / file_name
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_file, dest_file)
                    result["files_backed_up"] += 1
                except Exception as e:
                    result["errors"].append(f"Failed to backup {file_name}: {e}")
        
        result["size"] = self._calculate_directory_size(home_backup_path)
        return result
    
    def _backup_system_files(self, backup_path: Path) -> Dict:
        """Backup critical system files"""
        system_backup_path = backup_path / 'system'
        system_backup_path.mkdir(exist_ok=True)
        
        system_commands = [
            ('systemctl list-enabled --no-pager', 'enabled_services.txt'),
            ('systemctl list-active --no-pager', 'active_services.txt'),
            ('mount', 'mount_points.txt'),
            ('lsblk', 'block_devices.txt'),
            ('uname -a', 'kernel_info.txt'),
            ('lscpu', 'cpu_info.txt'),
            ('free -h', 'memory_info.txt'),
            ('df -h', 'disk_usage.txt')
        ]
        
        result = {
            "component": "system_files",
            "success": True,
            "files_backed_up": 0,
            "errors": [],
            "size": 0
        }
        
        # Execute system commands and save output
        for command, output_file in system_commands:
            try:
                output_path = system_backup_path / output_file
                with open(output_path, 'w') as f:
                    subprocess.run(command.split(), stdout=f, check=True)
                result["files_backed_up"] += 1
            except Exception as e:
                result["errors"].append(f"Failed to execute {command}: {e}")
        
        result["size"] = self._calculate_directory_size(system_backup_path)
        return result
    
    def _backup_custom_path(self, backup_path: Path, custom_path: str) -> Dict:
        """Backup custom specified path"""
        custom_backup_path = backup_path / 'custom' / Path(custom_path).name
        custom_backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        result = {
            "component": f"custom_path_{Path(custom_path).name}",
            "success": True,
            "files_backed_up": 0,
            "errors": [],
            "size": 0
        }
        
        try:
            if os.path.isdir(custom_path):
                shutil.copytree(custom_path, custom_backup_path, ignore_errors=True)
                result["files_backed_up"] = len(list(custom_backup_path.rglob('*')))
            elif os.path.isfile(custom_path):
                shutil.copy2(custom_path, custom_backup_path)
                result["files_backed_up"] = 1
            else:
                result["errors"].append(f"Path does not exist: {custom_path}")
                result["success"] = False
        except Exception as e:
            result["errors"].append(f"Failed to backup {custom_path}: {e}")
            result["success"] = False
        
        result["size"] = self._calculate_directory_size(custom_backup_path.parent)
        return result
    
    def _calculate_directory_size(self, directory: Path) -> int:
        """Calculate total size of directory in bytes"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except (OSError, FileNotFoundError):
                        pass
        except Exception:
            pass
        return total_size
    
    def _display_backup_summary(self, backup_info: Dict):
        """Display backup completion summary"""
        size_mb = backup_info["size"] / (1024 * 1024)
        
        # Create summary table
        table = Table(title="Backup Summary", box=box.ROUNDED)
        table.add_column("Component", style="cyan")
        table.add_column("Files", style="yellow")
        table.add_column("Size (MB)", style="green")
        table.add_column("Status", style="white")
        
        for component in backup_info["components"]:
            comp_size_mb = component["size"] / (1024 * 1024)
            status = "✅ Success" if component["success"] else "❌ Partial"
            
            table.add_row(
                component["component"].replace('_', ' ').title(),
                str(component["files_backed_up"]),
                f"{comp_size_mb:.1f}",
                status
            )
        
        self.console.print(table)
        
        # Overall summary
        status_color = "green" if backup_info["success"] else "yellow"
        self.console.print(Panel(
            f"[bold {status_color}]Backup Completed![/bold {status_color}]\n\n"
            f"Name: {backup_info['name']}\n"
            f"Total Files: {backup_info['files_count']:,}\n"
            f"Total Size: {size_mb:.1f} MB\n"
            f"Location: {backup_info['path']}\n"
            f"Errors: {len(backup_info['errors'])}\n\n"
            f"[dim]Backup completed at {datetime.fromtimestamp(backup_info['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}[/dim]",
            title="🎉 Backup Complete",
            border_style=status_color
        ))
    
    def schedule_backup(self, schedule_name: str, frequency: str, time_str: str,
                       backup_options: Dict) -> bool:
        """Schedule automatic backup"""
        schedule_id = hashlib.md5(schedule_name.encode()).hexdigest()[:8]
        
        schedule_config = {
            "id": schedule_id,
            "name": schedule_name,
            "frequency": frequency,
            "time": time_str,
            "options": backup_options,
            "created": time.time(),
            "last_run": None,
            "next_run": None,
            "enabled": True
        }
        
        # Add to schedules
        self.schedules[schedule_id] = schedule_config
        self._save_schedules()
        
        # Register with scheduler
        self._register_schedule(schedule_config)
        
        self.console.print(Panel(
            f"[bold green]Backup Scheduled Successfully![/bold green]\n\n"
            f"Name: {schedule_name}\n"
            f"Frequency: {frequency}\n"
            f"Time: {time_str}\n"
            f"Schedule ID: {schedule_id}\n\n"
            f"The backup will run automatically according to the schedule.",
            title="📅 Schedule Created",
            border_style="green"
        ))
        
        return True
    
    def _register_schedule(self, schedule_config: Dict):
        """Register schedule with the scheduler"""
        frequency = schedule_config["frequency"]
        time_str = schedule_config["time"]
        
        def backup_job():
            self.logger.info(f"Running scheduled backup: {schedule_config['name']}")
            try:
                backup_info = self.create_backup(
                    backup_name=f"{schedule_config['name']}-{datetime.now().strftime('%Y%m%d-%H%M')}",
                    **schedule_config["options"]
                )
                
                # Update last run time
                schedule_config["last_run"] = time.time()
                self.schedules[schedule_config["id"]] = schedule_config
                self._save_schedules()
                
                self.logger.info(f"Scheduled backup completed: {backup_info['name']}")
            except Exception as e:
                self.logger.error(f"Scheduled backup failed: {e}")
        
        # Schedule based on frequency
        if frequency == "daily":
            schedule.every().day.at(time_str).do(backup_job)
        elif frequency == "weekly":
            schedule.every().week.at(time_str).do(backup_job)
        elif frequency == "hourly":
            schedule.every().hour.do(backup_job)
        elif frequency.startswith("every_"):
            # Custom interval (e.g., "every_6_hours")
            parts = frequency.split('_')
            if len(parts) == 3:
                interval = int(parts[1])
                unit = parts[2]
                if unit == "hours":
                    schedule.every(interval).hours.do(backup_job)
                elif unit == "minutes":
                    schedule.every(interval).minutes.do(backup_job)
    
    def start_scheduler(self):
        """Start the backup scheduler daemon"""
        if self.scheduler_running:
            self.console.print("[yellow]Scheduler is already running[/yellow]")
            return
        
        self.scheduler_running = True
        
        # Load and register existing schedules
        for schedule_config in self.schedules.values():
            if schedule_config.get("enabled", True):
                self._register_schedule(schedule_config)
        
        def scheduler_loop():
            while self.scheduler_running:
                schedule.run_pending()
                time.sleep(30)  # Check every 30 seconds
        
        self.scheduler_thread = threading.Thread(target=scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        
        self.console.print(Panel(
            "[bold green]Backup Scheduler Started![/bold green]\n\n"
            f"Active schedules: {len([s for s in self.schedules.values() if s.get('enabled', True)])}\n"
            f"The scheduler is now running in the background.",
            title="📅 Scheduler Active",
            border_style="green"
        ))
        
        self.logger.info("Backup scheduler started")
    
    def stop_scheduler(self):
        """Stop the backup scheduler"""
        self.scheduler_running = False
        schedule.clear()
        
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
        
        self.console.print("[green]Backup scheduler stopped[/green]")
        self.logger.info("Backup scheduler stopped")
    
    def list_backups(self) -> List[Dict]:
        """List all available backups"""
        backups = []
        
        if not self.backup_dir.exists():
            return backups
        
        for backup_folder in self.backup_dir.iterdir():
            if backup_folder.is_dir():
                metadata_file = backup_folder / 'backup_info.json'
                
                if metadata_file.exists():
                    try:
                        with open(metadata_file, 'r') as f:
                            backup_info = json.load(f)
                            backups.append(backup_info)
                    except Exception as e:
                        self.logger.error(f"Error reading backup metadata: {e}")
                else:
                    # Create basic info for backups without metadata
                    backup_info = {
                        "name": backup_folder.name,
                        "timestamp": backup_folder.stat().st_mtime,
                        "path": str(backup_folder),
                        "size": self._calculate_directory_size(backup_folder),
                        "files_count": len(list(backup_folder.rglob('*'))),
                        "has_metadata": False
                    }
                    backups.append(backup_info)
        
        # Sort by timestamp (newest first)
        backups.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
        return backups
    
    def list_schedules(self) -> Dict:
        """List all backup schedules"""
        return self.schedules
    
    def remove_backup(self, backup_name: str) -> bool:
        """Remove a backup"""
        backup_path = self.backup_dir / backup_name
        
        if not backup_path.exists():
            self.console.print(f"[red]Backup not found: {backup_name}[/red]")
            return False
        
        try:
            shutil.rmtree(backup_path)
            self.console.print(f"[green]Backup removed: {backup_name}[/green]")
            self.logger.info(f"Backup removed: {backup_name}")
            return True
        except Exception as e:
            self.console.print(f"[red]Error removing backup: {e}[/red]")
            self.logger.error(f"Error removing backup {backup_name}: {e}")
            return False
    
    def remove_schedule(self, schedule_id: str) -> bool:
        """Remove a backup schedule"""
        if schedule_id not in self.schedules:
            self.console.print(f"[red]Schedule not found: {schedule_id}[/red]")
            return False
        
        try:
            del self.schedules[schedule_id]
            self._save_schedules()
            
            # Clear and re-register remaining schedules
            schedule.clear()
            for schedule_config in self.schedules.values():
                if schedule_config.get("enabled", True):
                    self._register_schedule(schedule_config)
            
            self.console.print(f"[green]Schedule removed: {schedule_id}[/green]")
            self.logger.info(f"Schedule removed: {schedule_id}")
            return True
        except Exception as e:
            self.console.print(f"[red]Error removing schedule: {e}[/red]")
            self.logger.error(f"Error removing schedule {schedule_id}: {e}")
            return False
    
    def display_backup_status(self):
        """Display comprehensive backup status"""
        backups = self.list_backups()
        schedules = self.list_schedules()
        
        # Backup list
        if backups:
            backup_table = Table(title="Available Backups", box=box.ROUNDED)
            backup_table.add_column("Name", style="cyan")
            backup_table.add_column("Date", style="yellow")
            backup_table.add_column("Size", style="green")
            backup_table.add_column("Files", style="blue")
            backup_table.add_column("Status", style="white")
            
            for backup in backups[:10]:  # Show latest 10
                backup_date = datetime.fromtimestamp(backup['timestamp']).strftime('%Y-%m-%d %H:%M')
                size_mb = backup['size'] / (1024 * 1024)
                status = "✅ Complete" if backup.get('success', True) else "⚠️ Partial"
                
                backup_table.add_row(
                    backup['name'][:30] + '...' if len(backup['name']) > 30 else backup['name'],
                    backup_date,
                    f"{size_mb:.1f} MB",
                    f"{backup['files_count']:,}" if 'files_count' in backup else "N/A",
                    status
                )
            
            self.console.print(backup_table)
        else:
            self.console.print("[yellow]No backups found[/yellow]")
        
        # Schedule list
        if schedules:
            schedule_table = Table(title="Backup Schedules", box=box.ROUNDED)
            schedule_table.add_column("Name", style="cyan")
            schedule_table.add_column("Frequency", style="yellow")
            schedule_table.add_column("Time", style="green")
            schedule_table.add_column("Last Run", style="blue")
            schedule_table.add_column("Status", style="white")
            
            for schedule_config in schedules.values():
                last_run = "Never" if not schedule_config.get('last_run') else \
                          datetime.fromtimestamp(schedule_config['last_run']).strftime('%Y-%m-%d %H:%M')
                status = "🟢 Enabled" if schedule_config.get('enabled', True) else "🔴 Disabled"
                
                schedule_table.add_row(
                    schedule_config['name'],
                    schedule_config['frequency'],
                    schedule_config['time'],
                    last_run,
                    status
                )
            
            self.console.print(schedule_table)
        else:
            self.console.print("[yellow]No scheduled backups[/yellow]")
        
        # Overall statistics
        total_backups = len(backups)
        total_size = sum(backup['size'] for backup in backups) / (1024 * 1024 * 1024)  # GB
        active_schedules = len([s for s in schedules.values() if s.get('enabled', True)])
        
        self.console.print(Panel(
            f"[bold blue]Backup System Statistics[/bold blue]\n\n"
            f"Total Backups: {total_backups}\n"
            f"Total Size: {total_size:.2f} GB\n"
            f"Active Schedules: {active_schedules}\n"
            f"Scheduler Status: {'🟢 Running' if self.scheduler_running else '🔴 Stopped'}\n"
            f"Backup Directory: {self.backup_dir}",
            title="📊 Statistics",
            border_style="blue"
        ))