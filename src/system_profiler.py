#!/usr/bin/env python3
"""
Advanced System Profiler for MX Tweaks Pro v2.1
Provides detailed hardware detection and system analysis
"""

import os
import platform
import subprocess
import psutil
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

@dataclass
class CPUInfo:
    """CPU information structure"""
    model: str
    cores: int
    threads: int
    base_freq: float
    max_freq: float
    cache_l1: str
    cache_l2: str
    cache_l3: str
    architecture: str
    features: List[str]
    governor: str
    scaling_driver: str

@dataclass
class MemoryInfo:
    """Memory information structure"""
    total_ram: int
    available_ram: int
    swap_total: int
    swap_used: int
    memory_type: str
    memory_speed: str
    memory_channels: int

@dataclass
class StorageInfo:
    """Storage device information"""
    device: str
    size: int
    model: str
    type: str  # SSD, HDD, NVMe
    interface: str
    scheduler: str
    rotational: bool
    read_speed: float
    write_speed: float

@dataclass
class SystemInfo:
    """Complete system information"""
    hostname: str
    kernel: str
    distro: str
    desktop_env: str
    boot_time: float
    uptime: float
    load_avg: List[float]
    cpu: CPUInfo
    memory: MemoryInfo
    storage: List[StorageInfo]
    network_interfaces: List[Dict]
    graphics: Dict
    temperature: Dict

class SystemProfiler:
    """Advanced system profiler with hardware detection"""
    
    def __init__(self, logger):
        self.logger = logger
        self.console = Console()
        self._system_info = None
    
    def get_cpu_info(self) -> CPUInfo:
        """Get detailed CPU information"""
        try:
            # Get CPU model and basic info
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
            
            model = "Unknown"
            features = []
            for line in cpuinfo.split('\n'):
                if 'model name' in line:
                    model = line.split(':')[1].strip()
                    break
                elif 'flags' in line:
                    features = line.split(':')[1].strip().split()
            
            # Get frequency info
            cpu_freq = psutil.cpu_freq()
            base_freq = cpu_freq.current if cpu_freq else 0
            max_freq = cpu_freq.max if cpu_freq else 0
            
            # Get governor and scaling driver
            governor = "unknown"
            scaling_driver = "unknown"
            try:
                with open('/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor', 'r') as f:
                    governor = f.read().strip()
                with open('/sys/devices/system/cpu/cpu0/cpufreq/scaling_driver', 'r') as f:
                    scaling_driver = f.read().strip()
            except FileNotFoundError:
                pass
            
            # Get cache info
            cache_l1 = cache_l2 = cache_l3 = "Unknown"
            try:
                cache_info = subprocess.run(['lscpu'], capture_output=True, text=True)
                for line in cache_info.stdout.split('\n'):
                    if 'L1d cache:' in line:
                        cache_l1 = line.split(':')[1].strip()
                    elif 'L2 cache:' in line:
                        cache_l2 = line.split(':')[1].strip()
                    elif 'L3 cache:' in line:
                        cache_l3 = line.split(':')[1].strip()
            except:
                pass
            
            return CPUInfo(
                model=model,
                cores=psutil.cpu_count(logical=False),
                threads=psutil.cpu_count(logical=True),
                base_freq=base_freq,
                max_freq=max_freq,
                cache_l1=cache_l1,
                cache_l2=cache_l2,
                cache_l3=cache_l3,
                architecture=platform.machine(),
                features=features[:10],  # Top 10 features
                governor=governor,
                scaling_driver=scaling_driver
            )
        except Exception as e:
            self.logger.error(f"Error getting CPU info: {e}")
            return CPUInfo(
                model="Unknown", cores=0, threads=0, base_freq=0, max_freq=0,
                cache_l1="Unknown", cache_l2="Unknown", cache_l3="Unknown",
                architecture="Unknown", features=[], governor="unknown",
                scaling_driver="unknown"
            )
    
    def get_memory_info(self) -> MemoryInfo:
        """Get detailed memory information"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Try to get memory type and speed
            memory_type = "Unknown"
            memory_speed = "Unknown"
            memory_channels = 1
            
            try:
                dmidecode = subprocess.run(['dmidecode', '-t', 'memory'], 
                                         capture_output=True, text=True)
                if dmidecode.returncode == 0:
                    for line in dmidecode.stdout.split('\n'):
                        if 'Type:' in line and 'DDR' in line:
                            memory_type = line.split(':')[1].strip()
                        elif 'Speed:' in line and 'MHz' in line:
                            memory_speed = line.split(':')[1].strip()
            except:
                pass
            
            return MemoryInfo(
                total_ram=memory.total,
                available_ram=memory.available,
                swap_total=swap.total,
                swap_used=swap.used,
                memory_type=memory_type,
                memory_speed=memory_speed,
                memory_channels=memory_channels
            )
        except Exception as e:
            self.logger.error(f"Error getting memory info: {e}")
            return MemoryInfo(0, 0, 0, 0, "Unknown", "Unknown", 1)
    
    def get_storage_info(self) -> List[StorageInfo]:
        """Get detailed storage device information"""
        storage_devices = []
        
        try:
            partitions = psutil.disk_partitions()
            processed_devices = set()
            
            for partition in partitions:
                device_name = partition.device
                if device_name in processed_devices:
                    continue
                
                # Extract base device name
                base_device = device_name.rstrip('0123456789')
                if base_device.endswith('p'):
                    base_device = base_device[:-1]
                
                device_short = base_device.split('/')[-1]
                
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    
                    # Determine if SSD or HDD
                    rotational_file = f"/sys/block/{device_short}/queue/rotational"
                    is_ssd = False
                    try:
                        with open(rotational_file, 'r') as f:
                            is_ssd = f.read().strip() == '0'
                    except:
                        pass
                    
                    # Get scheduler
                    scheduler_file = f"/sys/block/{device_short}/queue/scheduler"
                    scheduler = "unknown"
                    try:
                        with open(scheduler_file, 'r') as f:
                            sched_line = f.read().strip()
                            # Extract current scheduler (between brackets)
                            if '[' in sched_line and ']' in sched_line:
                                scheduler = sched_line.split('[')[1].split(']')[0]
                    except:
                        pass
                    
                    # Get device model
                    model_file = f"/sys/block/{device_short}/device/model"
                    model = "Unknown"
                    try:
                        with open(model_file, 'r') as f:
                            model = f.read().strip()
                    except:
                        pass
                    
                    # Determine interface type
                    interface = "SATA"
                    if 'nvme' in device_name.lower():
                        interface = "NVMe"
                    elif 'mmc' in device_name.lower():
                        interface = "eMMC"
                    
                    storage_devices.append(StorageInfo(
                        device=device_name,
                        size=usage.total,
                        model=model,
                        type="NVMe SSD" if interface == "NVMe" else ("SSD" if is_ssd else "HDD"),
                        interface=interface,
                        scheduler=scheduler,
                        rotational=not is_ssd,
                        read_speed=0.0,  # Would need benchmarking
                        write_speed=0.0  # Would need benchmarking
                    ))
                    
                    processed_devices.add(device_name)
                    
                except PermissionError:
                    continue
                except Exception as e:
                    self.logger.error(f"Error processing device {device_name}: {e}")
                    continue
        
        except Exception as e:
            self.logger.error(f"Error getting storage info: {e}")
        
        return storage_devices
    
    def get_graphics_info(self) -> Dict:
        """Get graphics card information"""
        graphics = {"cards": [], "driver": "unknown", "opengl": "unknown"}
        
        try:
            lspci = subprocess.run(['lspci', '-k'], capture_output=True, text=True)
            if lspci.returncode == 0:
                current_card = None
                for line in lspci.stdout.split('\n'):
                    if 'VGA compatible controller' in line or 'Display controller' in line:
                        current_card = line.split(': ')[1] if ': ' in line else line
                        graphics["cards"].append(current_card)
                    elif 'Kernel driver in use' in line and current_card:
                        graphics["driver"] = line.split(': ')[1]
        except:
            pass
        
        return graphics
    
    def get_temperature_info(self) -> Dict:
        """Get system temperature information"""
        temperatures = {}
        
        try:
            # Try to get CPU temperature
            temp_sensors = psutil.sensors_temperatures()
            for name, entries in temp_sensors.items():
                for entry in entries:
                    if entry.current:
                        temperatures[f"{name}_{entry.label or 'main'}"] = entry.current
        except:
            pass
        
        return temperatures
    
    def get_network_interfaces(self) -> List[Dict]:
        """Get network interface information"""
        interfaces = []
        
        try:
            net_if_stats = psutil.net_if_stats()
            net_if_addrs = psutil.net_if_addrs()
            
            for interface, stats in net_if_stats.items():
                if interface != 'lo':  # Skip loopback
                    interface_info = {
                        "name": interface,
                        "is_up": stats.isup,
                        "speed": stats.speed,
                        "mtu": stats.mtu,
                        "addresses": []
                    }
                    
                    if interface in net_if_addrs:
                        for addr in net_if_addrs[interface]:
                            interface_info["addresses"].append({
                                "family": addr.family.name,
                                "address": addr.address,
                                "netmask": addr.netmask,
                                "broadcast": addr.broadcast
                            })
                    
                    interfaces.append(interface_info)
        except Exception as e:
            self.logger.error(f"Error getting network info: {e}")
        
        return interfaces
    
    def profile_system(self) -> SystemInfo:
        """Create complete system profile"""
        if self._system_info is None:
            try:
                # Get boot time
                boot_time = psutil.boot_time()
                uptime = psutil.time.time() - boot_time
                
                # Get load average
                load_avg = list(os.getloadavg())
                
                # Get distro info
                try:
                    with open('/etc/os-release', 'r') as f:
                        os_info = f.read()
                    distro = "Unknown"
                    for line in os_info.split('\n'):
                        if line.startswith('PRETTY_NAME='):
                            distro = line.split('=')[1].strip('"')
                            break
                except:
                    distro = platform.system() + " " + platform.release()
                
                # Get desktop environment
                desktop_env = os.environ.get('DESKTOP_SESSION', 
                            os.environ.get('XDG_CURRENT_DESKTOP', 'Unknown'))
                
                self._system_info = SystemInfo(
                    hostname=platform.node(),
                    kernel=platform.release(),
                    distro=distro,
                    desktop_env=desktop_env,
                    boot_time=boot_time,
                    uptime=uptime,
                    load_avg=load_avg,
                    cpu=self.get_cpu_info(),
                    memory=self.get_memory_info(),
                    storage=self.get_storage_info(),
                    network_interfaces=self.get_network_interfaces(),
                    graphics=self.get_graphics_info(),
                    temperature=self.get_temperature_info()
                )
            except Exception as e:
                self.logger.error(f"Error profiling system: {e}")
                # Return minimal info on error
                self._system_info = SystemInfo(
                    hostname="Unknown", kernel="Unknown", distro="Unknown",
                    desktop_env="Unknown", boot_time=0, uptime=0, load_avg=[0, 0, 0],
                    cpu=self.get_cpu_info(), memory=self.get_memory_info(),
                    storage=[], network_interfaces=[], graphics={}, temperature={}
                )
        
        return self._system_info
    
    def show_detailed_profile(self):
        """Display detailed system profile"""
        profile = self.profile_system()
        
        # System Overview
        overview_table = Table(title="🖥️  System Overview", box=box.ROUNDED)
        overview_table.add_column("Property", style="cyan", width=20)
        overview_table.add_column("Value", style="white")
        
        overview_table.add_row("Hostname", profile.hostname)
        overview_table.add_row("Distribution", profile.distro)
        overview_table.add_row("Kernel", profile.kernel)
        overview_table.add_row("Desktop Environment", profile.desktop_env)
        overview_table.add_row("Uptime", f"{profile.uptime/3600:.1f} hours")
        overview_table.add_row("Load Average", f"{profile.load_avg[0]:.2f}, {profile.load_avg[1]:.2f}, {profile.load_avg[2]:.2f}")
        
        # CPU Details
        cpu_table = Table(title="🔧 CPU Information", box=box.ROUNDED)
        cpu_table.add_column("Property", style="cyan", width=20)
        cpu_table.add_column("Value", style="white")
        
        cpu_table.add_row("Model", profile.cpu.model)
        cpu_table.add_row("Architecture", profile.cpu.architecture)
        cpu_table.add_row("Cores/Threads", f"{profile.cpu.cores}/{profile.cpu.threads}")
        cpu_table.add_row("Base Frequency", f"{profile.cpu.base_freq:.0f} MHz")
        cpu_table.add_row("Max Frequency", f"{profile.cpu.max_freq:.0f} MHz")
        cpu_table.add_row("Governor", profile.cpu.governor)
        cpu_table.add_row("Scaling Driver", profile.cpu.scaling_driver)
        cpu_table.add_row("L1 Cache", profile.cpu.cache_l1)
        cpu_table.add_row("L2 Cache", profile.cpu.cache_l2)
        cpu_table.add_row("L3 Cache", profile.cpu.cache_l3)
        
        # Memory Details
        memory_table = Table(title="💾 Memory Information", box=box.ROUNDED)
        memory_table.add_column("Property", style="cyan", width=20)
        memory_table.add_column("Value", style="white")
        
        memory_table.add_row("Total RAM", f"{profile.memory.total_ram / (1024**3):.1f} GB")
        memory_table.add_row("Available RAM", f"{profile.memory.available_ram / (1024**3):.1f} GB")
        memory_table.add_row("Memory Type", profile.memory.memory_type)
        memory_table.add_row("Memory Speed", profile.memory.memory_speed)
        memory_table.add_row("Total Swap", f"{profile.memory.swap_total / (1024**3):.1f} GB" if profile.memory.swap_total > 0 else "Disabled")
        memory_table.add_row("Used Swap", f"{profile.memory.swap_used / (1024**3):.1f} GB" if profile.memory.swap_used > 0 else "None")
        
        # Storage Details
        storage_table = Table(title="💿 Storage Information", box=box.ROUNDED)
        storage_table.add_column("Device", style="cyan")
        storage_table.add_column("Type", style="yellow")
        storage_table.add_column("Size", style="green")
        storage_table.add_column("Model", style="white")
        storage_table.add_column("Interface", style="blue")
        storage_table.add_column("Scheduler", style="magenta")
        
        for storage in profile.storage:
            storage_table.add_row(
                storage.device,
                storage.type,
                f"{storage.size / (1024**3):.1f} GB",
                storage.model,
                storage.interface,
                storage.scheduler
            )
        
        # Display all tables
        self.console.print(overview_table)
        self.console.print()
        self.console.print(cpu_table)
        self.console.print()
        self.console.print(memory_table)
        self.console.print()
        self.console.print(storage_table)
        
        # Graphics and Network info
        if profile.graphics.get("cards"):
            graphics_info = "\n".join(profile.graphics["cards"])
            graphics_panel = Panel(graphics_info, title="🎮 Graphics Information", border_style="green")
            self.console.print()
            self.console.print(graphics_panel)
        
        if profile.temperature:
            temp_info = "\n".join([f"{k}: {v}°C" for k, v in profile.temperature.items()])
            temp_panel = Panel(temp_info, title="🌡️  Temperature Sensors", border_style="red")
            self.console.print()
            self.console.print(temp_panel)
    
    def get_optimization_recommendations(self) -> List[Dict]:
        """Get system-specific optimization recommendations"""
        profile = self.profile_system()
        recommendations = []
        
        # CPU recommendations
        if profile.cpu.governor != "performance":
            recommendations.append({
                "category": "CPU",
                "priority": "high",
                "title": "CPU Governor Optimization",
                "description": f"Current governor is '{profile.cpu.governor}'. Switch to 'performance' for better performance.",
                "action": "optimize_cpu_governor"
            })
        
        # Memory recommendations
        memory_usage = (profile.memory.total_ram - profile.memory.available_ram) / profile.memory.total_ram
        if memory_usage > 0.8:
            recommendations.append({
                "category": "Memory",
                "priority": "high",
                "title": "High Memory Usage",
                "description": f"Memory usage is {memory_usage*100:.1f}%. Consider memory optimization.",
                "action": "optimize_memory"
            })
        
        # Storage recommendations
        for storage in profile.storage:
            if storage.type in ["SSD", "NVMe SSD"] and storage.scheduler not in ["mq-deadline", "none"]:
                recommendations.append({
                    "category": "Storage",
                    "priority": "medium",
                    "title": f"SSD Scheduler Optimization ({storage.device})",
                    "description": f"SSD using '{storage.scheduler}' scheduler. 'mq-deadline' is better for SSDs.",
                    "action": "optimize_io_scheduler"
                })
            elif storage.type == "HDD" and storage.scheduler != "bfq":
                recommendations.append({
                    "category": "Storage",
                    "priority": "medium",
                    "title": f"HDD Scheduler Optimization ({storage.device})",
                    "description": f"HDD using '{storage.scheduler}' scheduler. 'bfq' is better for HDDs.",
                    "action": "optimize_io_scheduler"
                })
        
        # Swap recommendations
        if profile.memory.swap_total > 0 and any(s.type in ["SSD", "NVMe SSD"] for s in profile.storage):
            recommendations.append({
                "category": "Memory",
                "priority": "low",
                "title": "Swap on SSD",
                "description": "Swap is enabled on SSD. Consider disabling for longevity.",
                "action": "disable_swap"
            })
        
        return recommendations