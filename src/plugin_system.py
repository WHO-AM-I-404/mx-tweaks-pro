#!/usr/bin/env python3
"""
Plugin System for MX Tweaks Pro v2.1
Modular plugin architecture for extensibility
"""

import os
import sys
import importlib
import importlib.util
import json
import hashlib
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt
from rich.panel import Panel
from rich.table import Table
from rich import box

class PluginInterface(ABC):
    """Base interface for all MX Tweaks Pro plugins"""
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.console = Console()
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name"""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Plugin description"""
        pass
    
    @property
    @abstractmethod
    def author(self) -> str:
        """Plugin author"""
        pass
    
    @property
    def category(self) -> str:
        """Plugin category (default: 'general')"""
        return "general"
    
    @property
    def dependencies(self) -> List[str]:
        """List of required dependencies"""
        return []
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize plugin (called when loaded)"""
        pass
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Main plugin execution"""
        pass
    
    def cleanup(self) -> bool:
        """Cleanup resources (called when unloaded)"""
        return True
    
    def get_commands(self) -> Dict[str, Callable]:
        """Return dictionary of plugin commands"""
        return {}
    
    def get_config_schema(self) -> Dict:
        """Return plugin configuration schema"""
        return {}

class PluginManager:
    """Advanced plugin management system"""
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.console = Console()
        
        # Plugin directories
        self.plugins_dir = Path.home() / '.mx-tweaks-pro' / 'plugins'
        self.system_plugins_dir = Path('/usr/share/mx-tweaks-pro/plugins')
        self.config_dir = Path.home() / '.mx-tweaks-pro' / 'plugin-config'
        
        # Create directories
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Plugin registry
        self.loaded_plugins: Dict[str, PluginInterface] = {}
        self.available_plugins: Dict[str, Dict] = {}
        self.plugin_commands: Dict[str, Callable] = {}
        
        # Plugin metadata
        self.registry_file = self.config_dir / 'registry.json'
        self.settings_file = self.config_dir / 'settings.json'
        
        # Load plugin registry
        self.registry = self._load_registry()
        self.settings = self._load_settings()
        
        # Discover available plugins
        self._discover_plugins()
    
    def _load_registry(self) -> Dict:
        """Load plugin registry"""
        try:
            if self.registry_file.exists():
                with open(self.registry_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            self.logger.error(f"Error loading plugin registry: {e}")
            return {}
    
    def _save_registry(self):
        """Save plugin registry"""
        try:
            with open(self.registry_file, 'w') as f:
                json.dump(self.registry, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving plugin registry: {e}")
    
    def _load_settings(self) -> Dict:
        """Load plugin settings"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            return {"auto_load": [], "disabled": []}
        except Exception as e:
            self.logger.error(f"Error loading plugin settings: {e}")
            return {"auto_load": [], "disabled": []}
    
    def _save_settings(self):
        """Save plugin settings"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving plugin settings: {e}")
    
    def _discover_plugins(self):
        """Discover available plugins from plugin directories"""
        plugin_dirs = [self.plugins_dir]
        if self.system_plugins_dir.exists():
            plugin_dirs.append(self.system_plugins_dir)
        
        for plugin_dir in plugin_dirs:
            self._scan_directory_for_plugins(plugin_dir)
    
    def _scan_directory_for_plugins(self, directory: Path):
        """Scan directory for plugin files"""
        if not directory.exists():
            return
        
        # Look for Python files and plugin manifests
        for item in directory.iterdir():
            if item.is_file() and item.suffix == '.py' and not item.name.startswith('_'):
                self._analyze_plugin_file(item)
            elif item.is_dir():
                # Check for plugin directory with __init__.py or main.py
                init_file = item / '__init__.py'
                main_file = item / 'main.py'
                manifest_file = item / 'plugin.json'
                
                if init_file.exists() or main_file.exists():
                    plugin_info = self._analyze_plugin_directory(item)
                    if plugin_info:
                        self.available_plugins[plugin_info['id']] = plugin_info
    
    def _analyze_plugin_file(self, plugin_file: Path):
        """Analyze single plugin file"""
        try:
            plugin_id = plugin_file.stem
            plugin_info = {
                'id': plugin_id,
                'name': plugin_id.replace('_', ' ').title(),
                'file_path': str(plugin_file),
                'type': 'file',
                'version': '1.0.0',
                'description': 'Plugin loaded from file',
                'author': 'Unknown',
                'category': 'general',
                'dependencies': [],
                'discovered_at': plugin_file.stat().st_mtime
            }
            
            # Try to extract metadata from plugin docstring
            metadata = self._extract_plugin_metadata(plugin_file)
            if metadata:
                plugin_info.update(metadata)
            
            self.available_plugins[plugin_id] = plugin_info
            
        except Exception as e:
            self.logger.error(f"Error analyzing plugin file {plugin_file}: {e}")
    
    def _analyze_plugin_directory(self, plugin_dir: Path) -> Optional[Dict]:
        """Analyze plugin directory"""
        try:
            plugin_id = plugin_dir.name
            plugin_info = {
                'id': plugin_id,
                'name': plugin_id.replace('_', ' ').title(),
                'directory_path': str(plugin_dir),
                'type': 'directory',
                'version': '1.0.0',
                'description': 'Plugin loaded from directory',
                'author': 'Unknown',
                'category': 'general',
                'dependencies': [],
                'discovered_at': plugin_dir.stat().st_mtime
            }
            
            # Check for plugin manifest
            manifest_file = plugin_dir / 'plugin.json'
            if manifest_file.exists():
                try:
                    with open(manifest_file, 'r') as f:
                        manifest = json.load(f)
                        plugin_info.update(manifest)
                except Exception as e:
                    self.logger.warning(f"Error reading manifest for {plugin_dir}: {e}")
            
            # Check for main plugin file
            main_file = plugin_dir / 'main.py'
            init_file = plugin_dir / '__init__.py'
            
            if main_file.exists():
                plugin_info['main_file'] = str(main_file)
                metadata = self._extract_plugin_metadata(main_file)
            elif init_file.exists():
                plugin_info['main_file'] = str(init_file)
                metadata = self._extract_plugin_metadata(init_file)
            else:
                return None
            
            if metadata:
                plugin_info.update(metadata)
            
            return plugin_info
            
        except Exception as e:
            self.logger.error(f"Error analyzing plugin directory {plugin_dir}: {e}")
            return None
    
    def _extract_plugin_metadata(self, plugin_file: Path) -> Optional[Dict]:
        """Extract metadata from plugin file docstring and comments"""
        try:
            with open(plugin_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            metadata = {}
            
            # Look for plugin metadata in comments
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('# Plugin:'):
                    metadata['name'] = line.split(':', 1)[1].strip()
                elif line.startswith('# Version:'):
                    metadata['version'] = line.split(':', 1)[1].strip()
                elif line.startswith('# Description:'):
                    metadata['description'] = line.split(':', 1)[1].strip()
                elif line.startswith('# Author:'):
                    metadata['author'] = line.split(':', 1)[1].strip()
                elif line.startswith('# Category:'):
                    metadata['category'] = line.split(':', 1)[1].strip()
            
            return metadata if metadata else None
            
        except Exception as e:
            self.logger.warning(f"Error extracting metadata from {plugin_file}: {e}")
            return None
    
    def load_plugin(self, plugin_id: str) -> bool:
        """Load a specific plugin"""
        if plugin_id in self.loaded_plugins:
            self.console.print(f"[yellow]Plugin {plugin_id} is already loaded[/yellow]")
            return True
        
        if plugin_id not in self.available_plugins:
            self.console.print(f"[red]Plugin {plugin_id} not found[/red]")
            return False
        
        plugin_info = self.available_plugins[plugin_id]
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task(f"Loading plugin {plugin_id}...", total=None)
                
                # Load plugin module
                plugin_module = self._load_plugin_module(plugin_info)
                if not plugin_module:
                    return False
                
                # Find plugin class
                plugin_class = self._find_plugin_class(plugin_module)
                if not plugin_class:
                    self.console.print(f"[red]No valid plugin class found in {plugin_id}[/red]")
                    return False
                
                # Instantiate plugin
                plugin_instance = plugin_class(self.config, self.logger)
                
                # Initialize plugin
                if not plugin_instance.initialize():
                    self.console.print(f"[red]Failed to initialize plugin {plugin_id}[/red]")
                    return False
                
                # Register plugin
                self.loaded_plugins[plugin_id] = plugin_instance
                
                # Register plugin commands
                plugin_commands = plugin_instance.get_commands()
                for cmd_name, cmd_func in plugin_commands.items():
                    full_cmd_name = f"{plugin_id}.{cmd_name}"
                    self.plugin_commands[full_cmd_name] = cmd_func
                
                progress.update(task, completed=100)
            
            # Update registry
            self.registry[plugin_id] = {
                'loaded_at': __import__('time').time(),
                'version': plugin_instance.version,
                'status': 'loaded'
            }
            self._save_registry()
            
            self.console.print(f"[green]✅ Plugin loaded: {plugin_instance.name} v{plugin_instance.version}[/green]")
            self.logger.info(f"Plugin loaded: {plugin_id}")
            return True
            
        except Exception as e:
            self.console.print(f"[red]Error loading plugin {plugin_id}: {e}[/red]")
            self.logger.error(f"Error loading plugin {plugin_id}: {e}")
            return False
    
    def _load_plugin_module(self, plugin_info: Dict):
        """Load plugin module from file or directory"""
        try:
            if plugin_info['type'] == 'file':
                # Load from single file
                spec = importlib.util.spec_from_file_location(
                    plugin_info['id'], plugin_info['file_path']
                )
                module = importlib.util.module_from_spec(spec)
                sys.modules[plugin_info['id']] = module
                spec.loader.exec_module(module)
                return module
            
            elif plugin_info['type'] == 'directory':
                # Load from directory
                main_file = plugin_info.get('main_file')
                if not main_file:
                    return None
                
                spec = importlib.util.spec_from_file_location(
                    plugin_info['id'], main_file
                )
                module = importlib.util.module_from_spec(spec)
                sys.modules[plugin_info['id']] = module
                spec.loader.exec_module(module)
                return module
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error loading plugin module: {e}")
            return None
    
    def _find_plugin_class(self, module) -> Optional[type]:
        """Find plugin class in module"""
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            
            if (isinstance(attr, type) and 
                issubclass(attr, PluginInterface) and 
                attr != PluginInterface):
                return attr
        
        return None
    
    def unload_plugin(self, plugin_id: str) -> bool:
        """Unload a specific plugin"""
        if plugin_id not in self.loaded_plugins:
            self.console.print(f"[yellow]Plugin {plugin_id} is not loaded[/yellow]")
            return False
        
        try:
            plugin_instance = self.loaded_plugins[plugin_id]
            
            # Cleanup plugin
            plugin_instance.cleanup()
            
            # Remove from loaded plugins
            del self.loaded_plugins[plugin_id]
            
            # Remove plugin commands
            commands_to_remove = [cmd for cmd in self.plugin_commands.keys() 
                                if cmd.startswith(f"{plugin_id}.")]
            for cmd in commands_to_remove:
                del self.plugin_commands[cmd]
            
            # Update registry
            if plugin_id in self.registry:
                self.registry[plugin_id]['status'] = 'unloaded'
                self.registry[plugin_id]['unloaded_at'] = __import__('time').time()
            
            self._save_registry()
            
            self.console.print(f"[green]Plugin unloaded: {plugin_id}[/green]")
            self.logger.info(f"Plugin unloaded: {plugin_id}")
            return True
            
        except Exception as e:
            self.console.print(f"[red]Error unloading plugin {plugin_id}: {e}[/red]")
            self.logger.error(f"Error unloading plugin {plugin_id}: {e}")
            return False
    
    def reload_plugin(self, plugin_id: str) -> bool:
        """Reload a specific plugin"""
        if plugin_id in self.loaded_plugins:
            if not self.unload_plugin(plugin_id):
                return False
        
        # Re-discover plugins to get latest version
        self._discover_plugins()
        
        return self.load_plugin(plugin_id)
    
    def install_plugin(self, plugin_path: str) -> bool:
        """Install plugin from file or directory"""
        source_path = Path(plugin_path)
        
        if not source_path.exists():
            self.console.print(f"[red]Plugin source not found: {plugin_path}[/red]")
            return False
        
        try:
            if source_path.is_file():
                # Install single file plugin
                dest_path = self.plugins_dir / source_path.name
                __import__('shutil').copy2(source_path, dest_path)
                plugin_id = dest_path.stem
            
            elif source_path.is_dir():
                # Install directory plugin
                dest_path = self.plugins_dir / source_path.name
                if dest_path.exists():
                    __import__('shutil').rmtree(dest_path)
                __import__('shutil').copytree(source_path, dest_path)
                plugin_id = dest_path.name
            
            else:
                self.console.print(f"[red]Invalid plugin source: {plugin_path}[/red]")
                return False
            
            # Re-discover plugins
            self._discover_plugins()
            
            self.console.print(f"[green]Plugin installed: {plugin_id}[/green]")
            self.logger.info(f"Plugin installed: {plugin_id} from {plugin_path}")
            
            # Ask to load the plugin
            if Confirm.ask(f"Load plugin {plugin_id} now?"):
                self.load_plugin(plugin_id)
            
            return True
            
        except Exception as e:
            self.console.print(f"[red]Error installing plugin: {e}[/red]")
            self.logger.error(f"Error installing plugin from {plugin_path}: {e}")
            return False
    
    def remove_plugin(self, plugin_id: str) -> bool:
        """Remove/uninstall a plugin"""
        if plugin_id not in self.available_plugins:
            self.console.print(f"[red]Plugin {plugin_id} not found[/red]")
            return False
        
        # Unload if loaded
        if plugin_id in self.loaded_plugins:
            self.unload_plugin(plugin_id)
        
        plugin_info = self.available_plugins[plugin_id]
        
        try:
            if plugin_info['type'] == 'file':
                os.remove(plugin_info['file_path'])
            elif plugin_info['type'] == 'directory':
                __import__('shutil').rmtree(plugin_info['directory_path'])
            
            # Remove from available plugins
            del self.available_plugins[plugin_id]
            
            # Remove from registry
            if plugin_id in self.registry:
                del self.registry[plugin_id]
            
            self._save_registry()
            
            self.console.print(f"[green]Plugin removed: {plugin_id}[/green]")
            self.logger.info(f"Plugin removed: {plugin_id}")
            return True
            
        except Exception as e:
            self.console.print(f"[red]Error removing plugin: {e}[/red]")
            self.logger.error(f"Error removing plugin {plugin_id}: {e}")
            return False
    
    def list_plugins(self, loaded_only: bool = False) -> Dict[str, Dict]:
        """List available or loaded plugins"""
        if loaded_only:
            return {
                plugin_id: {
                    'instance': plugin,
                    'name': plugin.name,
                    'version': plugin.version,
                    'description': plugin.description,
                    'author': plugin.author,
                    'category': plugin.category
                }
                for plugin_id, plugin in self.loaded_plugins.items()
            }
        else:
            return self.available_plugins
    
    def execute_plugin_command(self, command: str, *args, **kwargs) -> Any:
        """Execute a plugin command"""
        if command not in self.plugin_commands:
            available_commands = list(self.plugin_commands.keys())
            self.console.print(f"[red]Command not found: {command}[/red]")
            if available_commands:
                self.console.print(f"Available commands: {', '.join(available_commands)}")
            return None
        
        try:
            return self.plugin_commands[command](*args, **kwargs)
        except Exception as e:
            self.console.print(f"[red]Error executing command {command}: {e}[/red]")
            self.logger.error(f"Error executing plugin command {command}: {e}")
            return None
    
    def display_plugin_status(self):
        """Display comprehensive plugin status"""
        available_plugins = self.list_plugins(loaded_only=False)
        loaded_plugins = self.list_plugins(loaded_only=True)
        
        # Available plugins table
        if available_plugins:
            available_table = Table(title="Available Plugins", box=box.ROUNDED)
            available_table.add_column("ID", style="cyan")
            available_table.add_column("Name", style="yellow")
            available_table.add_column("Version", style="green")
            available_table.add_column("Category", style="blue")
            available_table.add_column("Status", style="white")
            
            for plugin_id, plugin_info in available_plugins.items():
                status = "🟢 Loaded" if plugin_id in loaded_plugins else "⚪ Available"
                
                available_table.add_row(
                    plugin_id,
                    plugin_info.get('name', plugin_id),
                    plugin_info.get('version', 'Unknown'),
                    plugin_info.get('category', 'general'),
                    status
                )
            
            self.console.print(available_table)
        else:
            self.console.print("[yellow]No plugins found[/yellow]")
        
        # Plugin commands table
        if self.plugin_commands:
            commands_table = Table(title="Available Plugin Commands", box=box.ROUNDED)
            commands_table.add_column("Command", style="cyan")
            commands_table.add_column("Plugin", style="yellow")
            
            for command in sorted(self.plugin_commands.keys()):
                plugin_id = command.split('.')[0]
                commands_table.add_row(command, plugin_id)
            
            self.console.print(commands_table)
        
        # Statistics
        total_available = len(available_plugins)
        total_loaded = len(loaded_plugins)
        total_commands = len(self.plugin_commands)
        
        self.console.print(Panel(
            f"[bold blue]Plugin System Statistics[/bold blue]\n\n"
            f"Available Plugins: {total_available}\n"
            f"Loaded Plugins: {total_loaded}\n"
            f"Plugin Commands: {total_commands}\n"
            f"Plugin Directory: {self.plugins_dir}\n"
            f"System Plugins: {self.system_plugins_dir}",
            title="📊 Plugin Statistics",
            border_style="blue"
        ))
    
    def auto_load_plugins(self):
        """Auto-load plugins marked for auto-loading"""
        auto_load_list = self.settings.get('auto_load', [])
        
        if not auto_load_list:
            return
        
        self.console.print(f"[blue]Auto-loading {len(auto_load_list)} plugins...[/blue]")
        
        for plugin_id in auto_load_list:
            if plugin_id not in self.settings.get('disabled', []):
                self.load_plugin(plugin_id)
    
    def enable_auto_load(self, plugin_id: str):
        """Enable auto-loading for a plugin"""
        if plugin_id not in self.settings.get('auto_load', []):
            self.settings.setdefault('auto_load', []).append(plugin_id)
            self._save_settings()
            self.console.print(f"[green]Auto-load enabled for {plugin_id}[/green]")
    
    def disable_auto_load(self, plugin_id: str):
        """Disable auto-loading for a plugin"""
        auto_load_list = self.settings.get('auto_load', [])
        if plugin_id in auto_load_list:
            auto_load_list.remove(plugin_id)
            self._save_settings()
            self.console.print(f"[yellow]Auto-load disabled for {plugin_id}[/yellow]")

def create_plugin_manager(config, logger):
    """Create and return plugin manager instance"""
    return PluginManager(config, logger)