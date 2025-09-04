#!/usr/bin/env python3
"""
Real-time System Monitor for MX Tweaks Pro v2.1
Live system monitoring like task manager
"""

import os
import time
import threading
import psutil
from datetime import datetime
from typing import Dict, List, Optional
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.progress import Progress, BarColumn, TextColumn
from rich.text import Text
from rich import box

class RealtimeMonitor:
    """Real-time system monitoring with live updates"""
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.console = Console()
        self.running = False
        self.update_interval = 1.0  # seconds
        self.monitor_thread = None
        
        # System info cache
        self._system_info = {}
        self._process_list = []
        self._network_stats = {}
        self._disk_stats = {}
        self._update_lock = threading.Lock()
        
        # Initialize system info
        self._update_system_info()
    
    def start_monitoring(self, duration: Optional[int] = None):
        """Start real-time monitoring"""
        self.running = True
        
        try:
            with Live(self._create_dashboard(), refresh_per_second=2, screen=True) as live:
                start_time = time.time()
                
                while self.running:
                    if duration and (time.time() - start_time) > duration:
                        break
                    
                    # Update system information
                    self._update_system_info()
                    
                    # Update live display
                    live.update(self._create_dashboard())
                    
                    time.sleep(self.update_interval)
                    
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Monitoring stopped by user[/yellow]")
        finally:
            self.running = False
    
    def stop_monitoring(self):
        """Stop real-time monitoring"""
        self.running = False
    
    def _update_system_info(self):
        """Update all system information"""
        with self._update_lock:
            try:
                # CPU information
                self._system_info['cpu_percent'] = psutil.cpu_percent(interval=None)
                self._system_info['cpu_count'] = psutil.cpu_count()
                self._system_info['cpu_freq'] = psutil.cpu_freq()
                self._system_info['cpu_per_core'] = psutil.cpu_percent(percpu=True)
                
                # Memory information
                memory = psutil.virtual_memory()
                self._system_info['memory'] = {
                    'total': memory.total,
                    'available': memory.available,
                    'used': memory.used,
                    'percent': memory.percent,
                    'free': memory.free,
                    'buffers': getattr(memory, 'buffers', 0),
                    'cached': getattr(memory, 'cached', 0)
                }
                
                # Swap information
                swap = psutil.swap_memory()
                self._system_info['swap'] = {
                    'total': swap.total,
                    'used': swap.used,
                    'free': swap.free,
                    'percent': swap.percent
                }
                
                # Disk information
                self._disk_stats = {}
                for partition in psutil.disk_partitions():
                    try:
                        usage = psutil.disk_usage(partition.mountpoint)
                        io = psutil.disk_io_counters(perdisk=False)
                        self._disk_stats[partition.device] = {
                            'mountpoint': partition.mountpoint,
                            'fstype': partition.fstype,
                            'total': usage.total,
                            'used': usage.used,
                            'free': usage.free,
                            'percent': (usage.used / usage.total) * 100,
                            'read_bytes': io.read_bytes if io else 0,
                            'write_bytes': io.write_bytes if io else 0
                        }
                    except PermissionError:
                        continue
                
                # Network information
                net_io = psutil.net_io_counters()
                if net_io:
                    self._network_stats = {
                        'bytes_sent': net_io.bytes_sent,
                        'bytes_recv': net_io.bytes_recv,
                        'packets_sent': net_io.packets_sent,
                        'packets_recv': net_io.packets_recv
                    }
                
                # Top processes
                processes = []
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'memory_info', 'status']):
                    try:
                        processes.append(proc.info)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                # Sort by CPU usage and take top 10
                self._process_list = sorted(processes, key=lambda x: x['cpu_percent'] or 0, reverse=True)[:10]
                
                # System uptime and load
                boot_time = datetime.fromtimestamp(psutil.boot_time())
                self._system_info['uptime'] = datetime.now() - boot_time
                self._system_info['load_avg'] = os.getloadavg() if hasattr(os, 'getloadavg') else (0, 0, 0)
                
            except Exception as e:
                self.logger.error(f"Error updating system info: {e}")
    
    def _create_dashboard(self) -> Panel:
        """Create the main dashboard layout"""
        # Create individual panels
        cpu_panel = self._create_cpu_panel()
        memory_panel = self._create_memory_panel()
        disk_panel = self._create_disk_panel()
        network_panel = self._create_network_panel()
        processes_panel = self._create_processes_panel()
        system_panel = self._create_system_panel()
        
        # Arrange panels in columns
        top_row = Columns([cpu_panel, memory_panel], equal=True)
        middle_row = Columns([disk_panel, network_panel], equal=True)
        bottom_row = Columns([processes_panel, system_panel], equal=True)
        
        # Main layout
        dashboard = Panel(
            f"{top_row}\n{middle_row}\n{bottom_row}",
            title="[bold cyan]🖥️ MX Tweaks Pro - Real-time System Monitor[/bold cyan]",
            subtitle=f"[dim]Updated: {datetime.now().strftime('%H:%M:%S')} | Press Ctrl+C to exit[/dim]",
            border_style="bright_blue"
        )
        
        return dashboard
    
    def _create_cpu_panel(self) -> Panel:
        """Create CPU monitoring panel"""
        cpu_percent = self._system_info.get('cpu_percent', 0)
        cpu_count = self._system_info.get('cpu_count', 0)
        cpu_freq = self._system_info.get('cpu_freq')
        cpu_per_core = self._system_info.get('cpu_per_core', [])
        
        # CPU usage bar
        cpu_bar = self._create_progress_bar(cpu_percent, 100, "CPU Usage")
        
        # CPU frequency info
        freq_text = ""
        if cpu_freq:
            freq_text = f"\nFrequency: {cpu_freq.current:.0f} MHz"
            if cpu_freq.min and cpu_freq.max:
                freq_text += f" ({cpu_freq.min:.0f}-{cpu_freq.max:.0f})"
        
        # Per-core usage
        cores_text = ""
        if cpu_per_core:
            cores_text = "\n\nPer-Core Usage:\n"
            for i, usage in enumerate(cpu_per_core[:8]):  # Show max 8 cores
                cores_text += f"Core {i}: {usage:5.1f}%\n"
        
        content = f"{cpu_bar}{freq_text}{cores_text}"
        
        return Panel(
            content.strip(),
            title=f"[bold yellow]🔧 CPU ({cpu_count} cores)[/bold yellow]",
            border_style="yellow"
        )
    
    def _create_memory_panel(self) -> Panel:
        """Create memory monitoring panel"""
        memory = self._system_info.get('memory', {})
        swap = self._system_info.get('swap', {})
        
        if not memory:
            return Panel("Memory info unavailable", title="[bold red]💾 Memory[/bold red]")
        
        # Memory usage bar
        mem_bar = self._create_progress_bar(memory['used'], memory['total'], "RAM Usage")
        
        # Memory details
        mem_details = f"\nTotal: {self._format_bytes(memory['total'])}\n"
        mem_details += f"Used: {self._format_bytes(memory['used'])}\n"
        mem_details += f"Available: {self._format_bytes(memory['available'])}\n"
        
        if memory.get('buffers') or memory.get('cached'):
            mem_details += f"Buffers: {self._format_bytes(memory.get('buffers', 0))}\n"
            mem_details += f"Cached: {self._format_bytes(memory.get('cached', 0))}\n"
        
        # Swap information
        swap_text = ""
        if swap.get('total', 0) > 0:
            swap_bar = self._create_progress_bar(swap['used'], swap['total'], "Swap Usage")
            swap_text = f"\n{swap_bar}\nSwap: {self._format_bytes(swap['used'])}/{self._format_bytes(swap['total'])}"
        else:
            swap_text = "\nSwap: Disabled"
        
        content = f"{mem_bar}{mem_details}{swap_text}"
        
        return Panel(
            content.strip(),
            title="[bold green]💾 Memory[/bold green]",
            border_style="green"
        )
    
    def _create_disk_panel(self) -> Panel:
        """Create disk monitoring panel"""
        if not self._disk_stats:
            return Panel("Disk info unavailable", title="[bold red]💿 Disk[/bold red]")
        
        content = ""
        for device, stats in list(self._disk_stats.items())[:4]:  # Show max 4 disks
            # Disk usage bar
            disk_bar = self._create_progress_bar(stats['used'], stats['total'], f"{device}")
            
            # Disk details
            disk_info = f"{disk_bar}\n"
            disk_info += f"Mount: {stats['mountpoint']}\n"
            disk_info += f"Type: {stats['fstype']}\n"
            disk_info += f"Size: {self._format_bytes(stats['total'])}\n"
            disk_info += f"Used: {self._format_bytes(stats['used'])}\n"
            disk_info += f"Free: {self._format_bytes(stats['free'])}\n"
            
            content += disk_info + "\n"
        
        return Panel(
            content.strip(),
            title="[bold magenta]💿 Disk Usage[/bold magenta]",
            border_style="magenta"
        )
    
    def _create_network_panel(self) -> Panel:
        """Create network monitoring panel"""
        net_stats = self._network_stats
        
        if not net_stats:
            return Panel("Network info unavailable", title="[bold red]🌐 Network[/bold red]")
        
        content = "Network I/O Statistics:\n\n"
        content += f"📤 Bytes Sent: {self._format_bytes(net_stats['bytes_sent'])}\n"
        content += f"📥 Bytes Received: {self._format_bytes(net_stats['bytes_recv'])}\n"
        content += f"📦 Packets Sent: {net_stats['packets_sent']:,}\n"
        content += f"📦 Packets Received: {net_stats['packets_recv']:,}\n"
        
        # Network interfaces
        try:
            interfaces = psutil.net_if_addrs()
            content += f"\nActive Interfaces: {len(interfaces)}\n"
            for interface in list(interfaces.keys())[:3]:
                content += f"• {interface}\n"
        except Exception:
            pass
        
        return Panel(
            content.strip(),
            title="[bold cyan]🌐 Network[/bold cyan]",
            border_style="cyan"
        )
    
    def _create_processes_panel(self) -> Panel:
        """Create top processes panel"""
        if not self._process_list:
            return Panel("Process info unavailable", title="[bold red]⚙️ Processes[/bold red]")
        
        # Create processes table
        table = Table(show_header=True, box=box.SIMPLE)
        table.add_column("PID", style="cyan", width=8)
        table.add_column("Name", style="white", width=15)
        table.add_column("CPU%", style="yellow", width=8)
        table.add_column("Memory%", style="green", width=8)
        table.add_column("Status", style="blue", width=8)
        
        for proc in self._process_list[:8]:  # Show top 8 processes
            pid = str(proc.get('pid', 'N/A'))
            name = proc.get('name', 'N/A')[:15]
            cpu = f"{proc.get('cpu_percent', 0):.1f}"
            memory = f"{proc.get('memory_percent', 0):.1f}"
            status = proc.get('status', 'N/A')[:8]
            
            table.add_row(pid, name, cpu, memory, status)
        
        return Panel(
            table,
            title="[bold red]⚙️ Top Processes[/bold red]",
            border_style="red"
        )
    
    def _create_system_panel(self) -> Panel:
        """Create system information panel"""
        uptime = self._system_info.get('uptime', 'N/A')
        load_avg = self._system_info.get('load_avg', (0, 0, 0))
        
        # Format uptime
        if uptime != 'N/A':
            days = uptime.days
            hours, remainder = divmod(uptime.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            uptime_str = f"{days}d {hours}h {minutes}m"
        else:
            uptime_str = "N/A"
        
        # System information
        content = f"System Information:\n\n"
        content += f"🕐 Uptime: {uptime_str}\n"
        content += f"📊 Load Average:\n"
        content += f"   1min: {load_avg[0]:.2f}\n"
        content += f"   5min: {load_avg[1]:.2f}\n"
        content += f"  15min: {load_avg[2]:.2f}\n"
        
        # Process count
        try:
            process_count = len(list(psutil.process_iter()))
            content += f"\n⚙️ Total Processes: {process_count}\n"
        except Exception:
            pass
        
        # Temperature (if available)
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                content += f"\n🌡️ Temperature:\n"
                for name, entries in temps.items():
                    for entry in entries[:2]:  # Show max 2 temperature sensors
                        content += f"   {entry.label or name}: {entry.current:.1f}°C\n"
        except Exception:
            pass
        
        return Panel(
            content.strip(),
            title="[bold white]🖥️ System Info[/bold white]",
            border_style="white"
        )
    
    def _create_progress_bar(self, current: float, total: float, label: str) -> str:
        """Create a text-based progress bar"""
        if total == 0:
            percentage = 0
        else:
            percentage = (current / total) * 100
        
        # Determine color based on percentage
        if percentage < 50:
            color = "green"
        elif percentage < 80:
            color = "yellow"
        else:
            color = "red"
        
        # Create bar (20 characters wide)
        bar_width = 20
        filled = int((percentage / 100.0) * bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)
        
        return f"[{color}]{label}: {percentage:5.1f}% [{bar}][/{color}]"
    
    def _format_bytes(self, bytes_value: int) -> str:
        """Format bytes to human readable format"""
        if bytes_value == 0:
            return "0 B"
        
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        i = 0
        while bytes_value >= 1024 and i < len(units) - 1:
            bytes_value = bytes_value / 1024.0
            i += 1
        
        return f"{bytes_value:.1f} {units[i]}"
    
    def get_snapshot(self) -> Dict:
        """Get a snapshot of current system information"""
        self._update_system_info()
        
        with self._update_lock:
            return {
                'timestamp': datetime.now(),
                'cpu': self._system_info.get('cpu_percent', 0),
                'memory': self._system_info.get('memory', {}),
                'disk': self._disk_stats,
                'network': self._network_stats,
                'processes': self._process_list,
                'uptime': self._system_info.get('uptime'),
                'load_avg': self._system_info.get('load_avg')
            }
    
    def export_snapshot(self, filename: Optional[str] = None) -> Optional[str]:
        """Export current system snapshot to file"""
        if filename is None:
            filename = f"system_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        snapshot = self.get_snapshot()
        
        # Convert datetime objects to strings for JSON serialization
        import json
        
        def json_serializer(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif hasattr(obj, 'total_seconds'):  # timedelta
                return obj.total_seconds()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        try:
            with open(filename, 'w') as f:
                json.dump(snapshot, f, indent=2, default=json_serializer)
            
            self.console.print(f"[green]✅ Snapshot exported to: {filename}[/green]")
            return filename
        except Exception as e:
            self.console.print(f"[red]❌ Error exporting snapshot: {e}[/red]")
            return None

def create_realtime_monitor(config, logger):
    """Create and return realtime monitor instance"""
    return RealtimeMonitor(config, logger)