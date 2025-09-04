#!/usr/bin/env python3
"""
Advanced Tweaks Engine for MX Tweaks Pro v2.1
Intelligent system optimization with hardware-specific tweaks
"""

import os
import subprocess
import psutil
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt
from rich.panel import Panel
from rich.table import Table
from rich import box

class AdvancedTweaksEngine:
    """Advanced system optimization engine with intelligent detection"""
    
    def __init__(self, config, logger, profiler):
        self.config = config
        self.logger = logger
        self.profiler = profiler
        self.console = Console()
        self.system_info = profiler.profile_system()
    
    def execute_command(self, command: str, description: str, safe_mode: bool = True) -> bool:
        """Execute system command with error handling and logging"""
        try:
            # Create backup if in safe mode
            if safe_mode and self.config.getboolean('general', 'safe_mode', fallback=False):
                self.create_system_checkpoint(description)
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task(description, total=None)
                
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                progress.update(task, completed=100)
            
            if result.returncode == 0:
                self.console.print(f"[green]✅ {description} completed successfully[/green]")
                self.logger.info(f"Command executed: {command}")
                if result.stdout:
                    self.logger.debug(f"Output: {result.stdout}")
                return True
            else:
                self.console.print(f"[red]❌ {description} failed[/red]")
                self.logger.error(f"Command failed: {command} - {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.console.print(f"[red]⏱️ {description} timed out[/red]")
            self.logger.error(f"Command timeout: {command}")
            return False
        except Exception as e:
            self.console.print(f"[red]💥 Unexpected error in {description}: {e}[/red]")
            self.logger.error(f"Unexpected error: {e}")
            return False
    
    def create_system_checkpoint(self, operation: str):
        """Create system checkpoint before major operations"""
        try:
            from .backup_manager import BackupManager
            backup_manager = BackupManager(self.config, self.logger)
            
            critical_files = [
                '/etc/fstab',
                '/etc/sysctl.conf',
                '/etc/systemd/system.conf',
                '/etc/default/grub'
            ]
            
            backup_name = backup_manager.create_backup(f"pre_{operation.replace(' ', '_')}", critical_files)
            self.logger.info(f"Created system checkpoint: {backup_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to create checkpoint: {e}")
    
    def intelligent_cpu_optimization(self) -> bool:
        """Advanced CPU optimization based on hardware detection"""
        self.console.print("\n[bold cyan]🎯 Intelligent CPU Optimization[/bold cyan]")
        
        cpu_info = self.system_info.cpu
        recommendations = []
        
        # Governor optimization
        if cpu_info.governor != "performance":
            recommendations.append({
                "action": "set_cpu_governor",
                "params": {"governor": "performance"},
                "description": f"Switch from '{cpu_info.governor}' to 'performance' governor",
                "impact": "High performance gain, higher power consumption"
            })
        
        # Scaling driver optimization
        if "intel_pstate" in cpu_info.scaling_driver:
            recommendations.append({
                "action": "optimize_intel_pstate",
                "params": {},
                "description": "Optimize Intel P-State driver settings",
                "impact": "Better frequency scaling for Intel CPUs"
            })
        
        # CPU frequency scaling optimization
        if cpu_info.max_freq > 0:
            recommendations.append({
                "action": "optimize_cpu_frequency",
                "params": {"max_freq": cpu_info.max_freq},
                "description": "Optimize CPU frequency scaling parameters",
                "impact": "Improved performance and efficiency"
            })
        
        # Display recommendations
        if recommendations:
            table = Table(title="CPU Optimization Recommendations", box=box.ROUNDED)
            table.add_column("Optimization", style="cyan")
            table.add_column("Impact", style="yellow")
            table.add_column("Apply", style="green")
            
            for rec in recommendations:
                table.add_row(
                    rec["description"],
                    rec["impact"],
                    "✓ Recommended"
                )
            
            self.console.print(table)
            
            if Confirm.ask("\n[yellow]Apply recommended CPU optimizations?[/yellow]"):
                success_count = 0
                for rec in recommendations:
                    if self._apply_cpu_optimization(rec):
                        success_count += 1
                
                self.console.print(f"\n[bold green]🎉 Applied {success_count}/{len(recommendations)} CPU optimizations[/bold green]")
                return success_count == len(recommendations)
        else:
            self.console.print("[green]✅ CPU is already optimally configured[/green]")
            return True
        
        return False
    
    def _apply_cpu_optimization(self, recommendation: Dict) -> bool:
        """Apply specific CPU optimization"""
        action = recommendation["action"]
        params = recommendation["params"]
        
        if action == "set_cpu_governor":
            governor = params["governor"]
            return self.execute_command(
                f"echo {governor} | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor > /dev/null",
                f"Setting CPU governor to {governor}"
            )
        
        elif action == "optimize_intel_pstate":
            commands = [
                "echo 1 | sudo tee /sys/devices/system/cpu/intel_pstate/no_turbo > /dev/null",
                "echo 100 | sudo tee /sys/devices/system/cpu/intel_pstate/min_perf_pct > /dev/null"
            ]
            return all(self.execute_command(cmd, "Optimizing Intel P-State") for cmd in commands)
        
        elif action == "optimize_cpu_frequency":
            max_freq = params["max_freq"]
            return self.execute_command(
                f"echo {int(max_freq * 1000)} | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_max_freq > /dev/null",
                "Optimizing CPU frequency scaling"
            )
        
        return False
    
    def intelligent_memory_optimization(self) -> bool:
        """Advanced memory optimization with intelligent parameter tuning"""
        self.console.print("\n[bold cyan]🧠 Intelligent Memory Optimization[/bold cyan]")
        
        memory_info = self.system_info.memory
        total_ram_gb = memory_info.total_ram / (1024**3)
        
        # Calculate optimal parameters based on RAM size
        if total_ram_gb >= 16:
            swappiness = 5
            dirty_ratio = 20
            dirty_background_ratio = 10
        elif total_ram_gb >= 8:
            swappiness = 10
            dirty_ratio = 15
            dirty_background_ratio = 5
        else:
            swappiness = 20
            dirty_ratio = 10
            dirty_background_ratio = 3
        
        optimizations = [
            {
                "command": f"echo {swappiness} | sudo tee /proc/sys/vm/swappiness > /dev/null",
                "description": f"Set swappiness to {swappiness} (optimal for {total_ram_gb:.1f}GB RAM)",
                "sysctl": f"vm.swappiness={swappiness}"
            },
            {
                "command": f"echo {dirty_ratio} | sudo tee /proc/sys/vm/dirty_ratio > /dev/null",
                "description": f"Set dirty ratio to {dirty_ratio}% for better I/O performance",
                "sysctl": f"vm.dirty_ratio={dirty_ratio}"
            },
            {
                "command": f"echo {dirty_background_ratio} | sudo tee /proc/sys/vm/dirty_background_ratio > /dev/null",
                "description": f"Set background dirty ratio to {dirty_background_ratio}%",
                "sysctl": f"vm.dirty_background_ratio={dirty_background_ratio}"
            }
        ]
        
        # Show current vs recommended settings
        table = Table(title="Memory Optimization Parameters", box=box.ROUNDED)
        table.add_column("Parameter", style="cyan")
        table.add_column("Current", style="yellow")
        table.add_column("Recommended", style="green")
        table.add_column("Benefit", style="white")
        
        try:
            with open('/proc/sys/vm/swappiness', 'r') as f:
                current_swappiness = f.read().strip()
            with open('/proc/sys/vm/dirty_ratio', 'r') as f:
                current_dirty = f.read().strip()
            with open('/proc/sys/vm/dirty_background_ratio', 'r') as f:
                current_bg_dirty = f.read().strip()
            
            table.add_row("Swappiness", current_swappiness, str(swappiness), "Reduce swap usage")
            table.add_row("Dirty Ratio", current_dirty + "%", str(dirty_ratio) + "%", "Better I/O performance")
            table.add_row("BG Dirty Ratio", current_bg_dirty + "%", str(dirty_background_ratio) + "%", "Smoother background writes")
            
        except:
            table.add_row("Swappiness", "Unknown", str(swappiness), "Reduce swap usage")
            table.add_row("Dirty Ratio", "Unknown", str(dirty_ratio) + "%", "Better I/O performance")
            table.add_row("BG Dirty Ratio", "Unknown", str(dirty_background_ratio) + "%", "Smoother background writes")
        
        self.console.print(table)
        
        if Confirm.ask("\n[yellow]Apply memory optimizations?[/yellow]"):
            success_count = 0
            sysctl_entries = []
            
            for opt in optimizations:
                if self.execute_command(opt["command"], opt["description"]):
                    success_count += 1
                    sysctl_entries.append(opt["sysctl"])
            
            # Make changes persistent
            if success_count > 0 and Confirm.ask("Make these changes permanent? (add to /etc/sysctl.conf)"):
                self._make_sysctl_permanent(sysctl_entries)
            
            self.console.print(f"\n[bold green]🎉 Applied {success_count}/{len(optimizations)} memory optimizations[/bold green]")
            return success_count == len(optimizations)
        
        return False
    
    def intelligent_storage_optimization(self) -> bool:
        """Advanced storage optimization with per-device intelligence"""
        self.console.print("\n[bold cyan]💾 Intelligent Storage Optimization[/bold cyan]")
        
        storage_devices = self.system_info.storage
        if not storage_devices:
            self.console.print("[yellow]⚠️ No storage devices detected for optimization[/yellow]")
            return False
        
        # Display current storage configuration
        table = Table(title="Storage Device Analysis", box=box.ROUNDED)
        table.add_column("Device", style="cyan")
        table.add_column("Type", style="yellow")
        table.add_column("Current Scheduler", style="white")
        table.add_column("Recommended", style="green")
        table.add_column("Reason", style="blue")
        
        optimizations = []
        
        for storage in storage_devices:
            device_name = storage.device.split('/')[-1].rstrip('0123456789')
            
            # Determine optimal scheduler
            if storage.type in ["SSD", "NVMe SSD"]:
                optimal_scheduler = "mq-deadline"
                reason = "Better for SSDs (lower latency)"
            else:
                optimal_scheduler = "bfq"
                reason = "Better for HDDs (fairness)"
            
            table.add_row(
                storage.device,
                storage.type,
                storage.scheduler,
                optimal_scheduler,
                reason
            )
            
            if storage.scheduler != optimal_scheduler:
                optimizations.append({
                    "device": device_name,
                    "current": storage.scheduler,
                    "optimal": optimal_scheduler,
                    "type": storage.type
                })
        
        self.console.print(table)
        
        if optimizations:
            if Confirm.ask(f"\n[yellow]Optimize {len(optimizations)} storage device(s)?[/yellow]"):
                success_count = 0
                
                for opt in optimizations:
                    scheduler_path = f"/sys/block/{opt['device']}/queue/scheduler"
                    command = f"echo {opt['optimal']} | sudo tee {scheduler_path} > /dev/null"
                    description = f"Set {opt['device']} ({opt['type']}) scheduler to {opt['optimal']}"
                    
                    if self.execute_command(command, description):
                        success_count += 1
                
                # Additional SSD optimizations
                ssd_devices = [opt for opt in optimizations if "SSD" in opt["type"]]
                if ssd_devices:
                    self._apply_ssd_optimizations(ssd_devices)
                
                self.console.print(f"\n[bold green]🎉 Optimized {success_count}/{len(optimizations)} storage devices[/bold green]")
                return success_count == len(optimizations)
        else:
            self.console.print("[green]✅ All storage devices are already optimized[/green]")
            return True
        
        return False
    
    def _apply_ssd_optimizations(self, ssd_devices: List[Dict]):
        """Apply additional SSD-specific optimizations"""
        self.console.print("\n[bold blue]🚀 Applying SSD-specific optimizations[/bold blue]")
        
        ssd_tweaks = [
            {
                "command": "echo 1 | sudo tee /sys/block/*/queue/rotational > /dev/null",
                "description": "Disable rotational flag for all devices"
            },
            {
                "command": "echo deadline | sudo tee /sys/block/*/queue/scheduler > /dev/null",
                "description": "Ensure deadline scheduler for optimal SSD performance"
            }
        ]
        
        for tweak in ssd_tweaks:
            self.execute_command(tweak["command"], tweak["description"])
    
    def intelligent_network_optimization(self) -> bool:
        """Advanced network optimization based on interface detection"""
        self.console.print("\n[bold cyan]🌐 Intelligent Network Optimization[/bold cyan]")
        
        interfaces = self.system_info.network_interfaces
        if not interfaces:
            self.console.print("[yellow]⚠️ No network interfaces detected[/yellow]")
            return False
        
        # Display network interfaces
        table = Table(title="Network Interface Analysis", box=box.ROUNDED)
        table.add_column("Interface", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Speed", style="yellow")
        table.add_column("MTU", style="white")
        table.add_column("Optimization", style="blue")
        
        optimizations = []
        
        for interface in interfaces:
            status = "UP" if interface["is_up"] else "DOWN"
            speed = f"{interface['speed']} Mbps" if interface['speed'] > 0 else "Unknown"
            mtu = str(interface["mtu"])
            
            optimization = "None needed"
            if interface["is_up"] and interface["speed"] >= 1000:
                if interface["mtu"] < 1500:
                    optimization = "Increase MTU to 1500"
                    optimizations.append({
                        "interface": interface["name"],
                        "action": "set_mtu",
                        "value": 1500
                    })
                elif interface["speed"] >= 10000 and interface["mtu"] < 9000:
                    optimization = "Consider Jumbo frames (MTU 9000)"
                    optimizations.append({
                        "interface": interface["name"],
                        "action": "set_mtu",
                        "value": 9000
                    })
            
            table.add_row(
                interface["name"],
                f"[green]{status}[/green]" if status == "UP" else f"[red]{status}[/red]",
                speed,
                mtu,
                optimization
            )
        
        self.console.print(table)
        
        # Apply network optimizations
        if optimizations:
            if Confirm.ask(f"\n[yellow]Apply network optimizations to {len(optimizations)} interface(s)?[/yellow]"):
                success_count = 0
                
                for opt in optimizations:
                    if opt["action"] == "set_mtu":
                        command = f"sudo ip link set dev {opt['interface']} mtu {opt['value']}"
                        description = f"Set {opt['interface']} MTU to {opt['value']}"
                        
                        if self.execute_command(command, description):
                            success_count += 1
                
                # Apply general network optimizations
                self._apply_network_kernel_optimizations()
                
                self.console.print(f"\n[bold green]🎉 Applied network optimizations to {success_count}/{len(optimizations)} interfaces[/bold green]")
                return success_count == len(optimizations)
        else:
            self.console.print("[green]✅ Network interfaces are already optimized[/green]")
            return True
        
        return False
    
    def _apply_network_kernel_optimizations(self):
        """Apply kernel-level network optimizations"""
        network_tweaks = [
            "net.core.rmem_max = 16777216",
            "net.core.wmem_max = 16777216",
            "net.ipv4.tcp_rmem = 4096 65536 16777216",
            "net.ipv4.tcp_wmem = 4096 65536 16777216",
            "net.ipv4.tcp_congestion_control = bbr"
        ]
        
        for tweak in network_tweaks:
            param, value = tweak.split(" = ")
            command = f"echo '{value}' | sudo tee /proc/sys/{param.replace('.', '/')} > /dev/null"
            self.execute_command(command, f"Set {param}")
    
    def _make_sysctl_permanent(self, entries: List[str]):
        """Add sysctl entries to make them permanent"""
        try:
            sysctl_file = "/etc/sysctl.d/99-mx-tweaks-pro.conf"
            
            # Create header comment
            header = [
                "# MX Tweaks Pro v2.1 - System Optimizations",
                f"# Generated on {time.strftime('%Y-%m-%d %H:%M:%S')}",
                "# These optimizations are applied for better system performance",
                ""
            ]
            
            # Write to sysctl config
            content = "\n".join(header + entries)
            command = f"echo '{content}' | sudo tee {sysctl_file} > /dev/null"
            
            if self.execute_command(command, "Making optimizations permanent"):
                self.execute_command("sudo sysctl -p {sysctl_file}", "Applying permanent settings")
                self.console.print(f"[green]✅ Optimizations saved to {sysctl_file}[/green]")
            
        except Exception as e:
            self.logger.error(f"Failed to make sysctl permanent: {e}")
    
    def run_comprehensive_optimization(self) -> Dict:
        """Run all intelligent optimizations with progress tracking"""
        self.console.print(Panel(
            "[bold cyan]MX Tweaks Pro v2.1 - Comprehensive System Optimization[/bold cyan]\n"
            "This will analyze your system and apply intelligent optimizations\n"
            "based on your hardware configuration.",
            title="🚀 Starting Intelligent Optimization",
            border_style="bright_blue"
        ))
        
        results = {
            "timestamp": time.time(),
            "optimizations_applied": [],
            "total_score_before": 0,
            "total_score_after": 0
        }
        
        # Run optimizations
        optimizations = [
            ("CPU", self.intelligent_cpu_optimization),
            ("Memory", self.intelligent_memory_optimization),
            ("Storage", self.intelligent_storage_optimization),
            ("Network", self.intelligent_network_optimization)
        ]
        
        success_count = 0
        for name, optimization_func in optimizations:
            self.console.print(f"\n[bold yellow]🔧 {name} Optimization[/bold yellow]")
            
            try:
                if optimization_func():
                    results["optimizations_applied"].append(name)
                    success_count += 1
                    self.console.print(f"[green]✅ {name} optimization completed[/green]")
                else:
                    self.console.print(f"[yellow]⚠️ {name} optimization skipped or failed[/yellow]")
            except Exception as e:
                self.logger.error(f"Error in {name} optimization: {e}")
                self.console.print(f"[red]❌ {name} optimization failed: {e}[/red]")
        
        # Final summary
        self.console.print(Panel(
            f"[bold green]Optimization Complete![/bold green]\n\n"
            f"Successfully applied: {success_count}/{len(optimizations)} optimizations\n"
            f"Optimized components: {', '.join(results['optimizations_applied'])}",
            title="🎉 Optimization Results",
            border_style="green"
        ))
        
        results["success_rate"] = success_count / len(optimizations)
        return results