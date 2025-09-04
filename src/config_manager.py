#!/usr/bin/env python3
"""
Config Manager untuk MX Tweaks Pro
Mengelola konfigurasi aplikasi dengan root access detection
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from configparser import ConfigParser
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm

class ConfigManager:
    def __init__(self):
        self.config_dir = Path.home() / '.config' / 'mx-tweaks-pro'
        self.config_file = self.config_dir / 'config.ini'
        self.backup_dir = self.config_dir / 'backups'
        self.console = Console()
        
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
    
    def check_root_access(self) -> bool:
        """Check if running with root privileges"""
        return os.geteuid() == 0
    
    def require_root_access(self, operation_name: str = "this operation") -> bool:
        """
        Check root access and handle accordingly
        Returns True if root access is available, False otherwise
        """
        console = Console()
        
        if self.check_root_access():
            return True
        
        # Display error message
        console.print(Panel(
            f"[bold red]❌ Root access is required for {operation_name}[/bold red]\n\n"
            f"[yellow]Please run with:[/yellow]\n"
            f"[cyan]sudo mx-tweaks-pro[/cyan]\n\n"
            f"[dim]Or for GUI applications:[/dim]\n"
            f"[cyan]pkexec mx-tweaks-pro --gui[/cyan]",
            title="🔒 Root Access Required",
            border_style="red"
        ))
        
        # Ask if user wants to try with pkexec
        if self._is_display_available():
            try:
                if Confirm.ask("\n[yellow]Would you like to try running with pkexec (GUI sudo)?[/yellow]"):
                    return self._restart_with_pkexec()
            except KeyboardInterrupt:
                console.print("\n[yellow]Operation cancelled by user[/yellow]")
                return False
        
        return False
    
    def _is_display_available(self) -> bool:
        """Check if GUI display is available for pkexec"""
        return os.environ.get('DISPLAY') is not None or os.environ.get('WAYLAND_DISPLAY') is not None
    
    def _restart_with_pkexec(self) -> bool:
        """Restart the application with pkexec"""
        console = Console()
        
        try:
            # Get current script arguments
            script_path = sys.argv[0]
            script_args = sys.argv[1:]
            
            # Construct pkexec command
            if script_path.startswith('./'):
                # If running from current directory, use absolute path
                script_path = os.path.abspath(script_path)
            elif not script_path.startswith('/'):
                # If it's just the command name, find it in PATH
                script_path = '/usr/local/bin/mx-tweaks-pro'
            
            pkexec_cmd = ['pkexec', script_path] + script_args
            
            console.print(f"[blue]Starting with pkexec...[/blue]")
            
            # Execute with pkexec
            result = subprocess.run(pkexec_cmd, capture_output=False)
            
            # Exit the current process since pkexec started a new one
            sys.exit(result.returncode)
            
        except FileNotFoundError:
            console.print("[red]❌ pkexec not found. Please install policykit or run with sudo.[/red]")
            return False
        except subprocess.CalledProcessError as e:
            console.print(f"[red]❌ Failed to start with pkexec: {e}[/red]")
            return False
        except Exception as e:
            console.print(f"[red]❌ Error: {e}[/red]")
            return False
    
    def check_operation_permissions(self, operation: str) -> bool:
        """
        Check if specific operation requires root and if we have permission
        Returns True if operation can proceed, False otherwise
        """
        # Define operations that require root access
        root_required_operations = {
            'system_cleanup': 'system cleanup operations',
            'package_management': 'package management operations',
            'service_management': 'service management operations',
            'system_configuration': 'system configuration changes',
            'security_hardening': 'security hardening operations',
            'network_optimization': 'network configuration changes',
            'performance_tweaks': 'performance optimization',
            'boot_optimization': 'boot configuration changes',
            'firewall_configuration': 'firewall configuration',
            'ssh_hardening': 'SSH configuration changes'
        }
        
        # Define operations that don't require root
        user_operations = {
            'appearance_tweaks': 'appearance customization',
            'user_backup': 'user data backup',
            'system_information': 'system information display',
            'plugin_management': 'plugin management',
            'configuration_view': 'configuration viewing'
        }
        
        if operation in root_required_operations:
            return self.require_root_access(root_required_operations[operation])
        elif operation in user_operations:
            # These operations can run without root
            return True
        else:
            # Unknown operation, assume root required for safety
            return self.require_root_access(f"operation: {operation}")
    
    def display_permission_info(self):
        """Display information about current permissions and available operations"""
        console = Console()
        
        is_root = self.check_root_access()
        
        if is_root:
            console.print(Panel(
                "[bold green]✅ Running with root privileges[/bold green]\n\n"
                "[green]All operations are available:[/green]\n"
                "• System cleanup and optimization\n"
                "• Package management\n"
                "• Service configuration\n"
                "• Security hardening\n"
                "• Network optimization\n"
                "• Appearance customization\n"
                "• Backup and restore\n"
                "• Plugin management",
                title="🔓 Root Access Detected",
                border_style="green"
            ))
        else:
            console.print(Panel(
                "[bold yellow]⚠️ Running with user privileges[/bold yellow]\n\n"
                "[green]Available operations:[/green]\n"
                "• Appearance customization\n"
                "• User data backup\n"
                "• System information display\n"
                "• Plugin management\n"
                "• Configuration viewing\n\n"
                "[red]Restricted operations (require sudo):[/red]\n"
                "• System cleanup and optimization\n"
                "• Package management\n"
                "• Service configuration\n"
                "• Security hardening\n"
                "• Network optimization\n\n"
                "[cyan]Run with: sudo mx-tweaks-pro[/cyan]",
                title="🔒 User Mode",
                border_style="yellow"
            ))