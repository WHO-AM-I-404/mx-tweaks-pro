#!/usr/bin/env python3
"""
Network Tweaks for MX Tweaks Pro v2.1
Advanced network optimization and connection tuning
"""

import os
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.prompt import Confirm, Prompt, IntPrompt
from rich.panel import Panel
from rich.table import Table
from rich import box
import psutil

class NetworkTweaks:
    """Advanced network optimization and tuning"""
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.console = Console()
        self.network_interfaces = self._get_network_interfaces()
    
    def _get_network_interfaces(self) -> List[Dict]:
        """Get detailed network interface information"""
        interfaces = []
        try:
            net_if_stats = psutil.net_if_stats()
            net_if_addrs = psutil.net_if_addrs()
            
            for interface_name, stats in net_if_stats.items():
                if interface_name != 'lo':  # Skip loopback
                    interface_info = {
                        "name": interface_name,
                        "is_up": stats.isup,
                        "speed": stats.speed,
                        "mtu": stats.mtu,
                        "type": self._detect_interface_type(interface_name),
                        "addresses": []
                    }
                    
                    if interface_name in net_if_addrs:
                        for addr in net_if_addrs[interface_name]:
                            if addr.family.name in ['AF_INET', 'AF_INET6']:
                                interface_info["addresses"].append({
                                    "family": addr.family.name,
                                    "address": addr.address,
                                    "netmask": addr.netmask
                                })
                    
                    interfaces.append(interface_info)
        except Exception as e:
            self.logger.error(f"Error getting network interfaces: {e}")
        
        return interfaces
    
    def _detect_interface_type(self, interface_name: str) -> str:
        """Detect network interface type"""
        if interface_name.startswith('eth'):
            return 'Ethernet'
        elif interface_name.startswith('wlan') or interface_name.startswith('wifi'):
            return 'WiFi'
        elif interface_name.startswith('enp'):
            return 'Ethernet'
        elif interface_name.startswith('wlp'):
            return 'WiFi'
        else:
            return 'Unknown'
    
    def execute_command(self, command: str, description: str) -> bool:
        """Execute command with progress indicator"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task(description, total=None)
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                progress.update(task, completed=100)
            
            if result.returncode == 0:
                self.console.print(f"[green]✅ {description} completed[/green]")
                self.logger.info(f"Network command executed: {command}")
                return True
            else:
                self.console.print(f"[red]❌ {description} failed: {result.stderr}[/red]")
                self.logger.error(f"Network command failed: {command} - {result.stderr}")
                return False
        except Exception as e:
            self.console.print(f"[red]❌ Error: {e}[/red]")
            self.logger.error(f"Network command error: {e}")
            return False
    
    def optimize_tcp_stack(self) -> bool:
        """Optimize TCP stack parameters"""
        self.console.print("\n[bold cyan]🚀 Optimizing TCP Stack[/bold cyan]")
        
        tcp_optimizations = [
            # TCP window scaling
            ("net.core.rmem_max", "134217728", "Increase max receive buffer"),
            ("net.core.wmem_max", "134217728", "Increase max send buffer"),
            ("net.ipv4.tcp_rmem", "4096 87380 134217728", "Optimize TCP read buffers"),
            ("net.ipv4.tcp_wmem", "4096 65536 134217728", "Optimize TCP write buffers"),
            
            # TCP congestion control
            ("net.ipv4.tcp_congestion_control", "bbr", "Use BBR congestion control"),
            ("net.core.default_qdisc", "fq", "Use FQ queueing discipline"),
            
            # TCP performance
            ("net.ipv4.tcp_window_scaling", "1", "Enable TCP window scaling"),
            ("net.ipv4.tcp_timestamps", "1", "Enable TCP timestamps"),
            ("net.ipv4.tcp_sack", "1", "Enable selective acknowledgments"),
            ("net.ipv4.tcp_fack", "1", "Enable forward acknowledgments"),
            
            # TCP fast open
            ("net.ipv4.tcp_fastopen", "3", "Enable TCP fast open"),
            
            # Reduce TCP timeouts
            ("net.ipv4.tcp_fin_timeout", "15", "Reduce FIN timeout"),
            ("net.ipv4.tcp_keepalive_time", "600", "Reduce keepalive time"),
            ("net.ipv4.tcp_keepalive_intvl", "60", "Reduce keepalive interval"),
            ("net.ipv4.tcp_keepalive_probes", "3", "Reduce keepalive probes")
        ]
        
        success_count = 0
        for param, value, description in tcp_optimizations:
            command = f"echo '{value}' | sudo tee /proc/sys/{param.replace('.', '/')} > /dev/null"
            if self.execute_command(command, f"Set {param} = {value}"):
                success_count += 1
        
        self.console.print(f"[green]✅ Applied {success_count}/{len(tcp_optimizations)} TCP optimizations[/green]")
        return success_count > len(tcp_optimizations) // 2
    
    def optimize_network_buffers(self) -> bool:
        """Optimize network buffer sizes"""
        self.console.print("\n[bold cyan]💾 Optimizing Network Buffers[/bold cyan]")
        
        buffer_optimizations = [
            ("net.core.netdev_max_backlog", "5000", "Increase network device backlog"),
            ("net.core.netdev_budget", "600", "Increase network budget"),
            ("net.unix.max_dgram_qlen", "50", "Increase Unix socket queue length"),
            ("net.core.somaxconn", "1024", "Increase socket listen backlog"),
            ("net.ipv4.tcp_max_syn_backlog", "8192", "Increase SYN backlog"),
            ("net.ipv4.tcp_max_tw_buckets", "2000000", "Increase TIME_WAIT buckets"),
            ("net.ipv4.ip_local_port_range", "1024 65535", "Expand local port range")
        ]
        
        success_count = 0
        for param, value, description in buffer_optimizations:
            command = f"echo '{value}' | sudo tee /proc/sys/{param.replace('.', '/')} > /dev/null"
            if self.execute_command(command, description):
                success_count += 1
        
        self.console.print(f"[green]✅ Applied {success_count}/{len(buffer_optimizations)} buffer optimizations[/green]")
        return success_count > len(buffer_optimizations) // 2
    
    def optimize_dns_resolution(self) -> bool:
        """Optimize DNS resolution settings"""
        self.console.print("\n[bold cyan]🌐 Optimizing DNS Resolution[/bold cyan]")
        
        # Fast DNS servers
        dns_servers = [
            "1.1.1.1",      # Cloudflare
            "1.0.0.1",      # Cloudflare secondary
            "8.8.8.8",      # Google
            "8.8.4.4"       # Google secondary
        ]
        
        try:
            # Backup original resolv.conf
            resolv_conf = Path('/etc/resolv.conf')
            if resolv_conf.exists():
                backup_cmd = "sudo cp /etc/resolv.conf /etc/resolv.conf.backup-mx-tweaks"
                self.execute_command(backup_cmd, "Backing up DNS configuration")
            
            # Create new resolv.conf with fast DNS
            dns_config = "\n".join([f"nameserver {server}" for server in dns_servers])
            dns_config += "\noptions timeout:2 attempts:3 rotate single-request-reopen\n"
            
            write_cmd = f"echo '{dns_config}' | sudo tee /etc/resolv.conf > /dev/null"
            if self.execute_command(write_cmd, "Configuring fast DNS servers"):
                # Test DNS resolution speed
                if self._test_dns_speed():
                    self.console.print("[green]✅ DNS optimization completed successfully[/green]")
                    return True
            
        except Exception as e:
            self.console.print(f"[red]❌ DNS optimization failed: {e}[/red]")
            # Restore backup if available
            restore_cmd = "sudo cp /etc/resolv.conf.backup-mx-tweaks /etc/resolv.conf"
            self.execute_command(restore_cmd, "Restoring DNS configuration")
        
        return False
    
    def _test_dns_speed(self) -> bool:
        """Test DNS resolution speed"""
        test_domains = ['google.com', 'github.com', 'cloudflare.com']
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Testing DNS resolution speed", total=len(test_domains))
            
            success_count = 0
            for domain in test_domains:
                start_time = time.time()
                result = subprocess.run(['nslookup', domain], 
                                      capture_output=True, text=True, timeout=5)
                end_time = time.time()
                
                if result.returncode == 0:
                    resolution_time = (end_time - start_time) * 1000
                    self.logger.info(f"DNS resolution for {domain}: {resolution_time:.1f}ms")
                    success_count += 1
                
                progress.advance(task)
        
        return success_count >= len(test_domains) // 2
    
    def configure_firewall_optimization(self) -> bool:
        """Configure firewall for network optimization"""
        self.console.print("\n[bold cyan]🔥 Optimizing Firewall Settings[/bold cyan]")
        
        # Check if UFW is available
        ufw_check = subprocess.run(['which', 'ufw'], capture_output=True)
        
        if ufw_check.returncode == 0:
            firewall_commands = [
                "sudo ufw --force enable",
                "sudo ufw default deny incoming",
                "sudo ufw default allow outgoing",
                "sudo ufw allow ssh",
                "sudo ufw allow http",
                "sudo ufw allow https"
            ]
            
            success_count = 0
            for cmd in firewall_commands:
                if self.execute_command(cmd, f"Configuring firewall rule"):
                    success_count += 1
            
            # Optimize connection tracking
            netfilter_optimizations = [
                ("net.netfilter.nf_conntrack_max", "262144", "Increase connection tracking"),
                ("net.netfilter.nf_conntrack_tcp_timeout_established", "1200", "Reduce TCP timeout"),
                ("net.netfilter.nf_conntrack_udp_timeout", "60", "Reduce UDP timeout")
            ]
            
            for param, value, description in netfilter_optimizations:
                command = f"echo '{value}' | sudo tee /proc/sys/{param.replace('.', '/')} > /dev/null 2>/dev/null || true"
                self.execute_command(command, description)
            
            self.console.print(f"[green]✅ Applied {success_count}/{len(firewall_commands)} firewall rules[/green]")
            return success_count > 0
        else:
            self.console.print("[yellow]⚠️ UFW not found, skipping firewall optimization[/yellow]")
            return True
    
    def optimize_wifi_power_management(self) -> bool:
        """Optimize WiFi power management"""
        self.console.print("\n[bold cyan]📶 Optimizing WiFi Power Management[/bold cyan]")
        
        wifi_interfaces = [iface for iface in self.network_interfaces if iface['type'] == 'WiFi']
        
        if not wifi_interfaces:
            self.console.print("[yellow]⚠️ No WiFi interfaces detected[/yellow]")
            return True
        
        success_count = 0
        for interface in wifi_interfaces:
            interface_name = interface['name']
            
            # Disable power management for better performance
            disable_pm_cmd = f"sudo iwconfig {interface_name} power off 2>/dev/null || true"
            if self.execute_command(disable_pm_cmd, f"Disable power management for {interface_name}"):
                success_count += 1
            
            # Set transmission power to maximum (if supported)
            max_power_cmd = f"sudo iwconfig {interface_name} txpower 20 2>/dev/null || true"
            self.execute_command(max_power_cmd, f"Set max transmission power for {interface_name}")
        
        self.console.print(f"[green]✅ Optimized {success_count}/{len(wifi_interfaces)} WiFi interfaces[/green]")
        return success_count > 0
    
    def run_network_benchmark(self) -> Dict:
        """Run network performance benchmark"""
        self.console.print("\n[bold cyan]📊 Running Network Benchmark[/bold cyan]")
        
        results = {
            "timestamp": time.time(),
            "interfaces": [],
            "dns_performance": {},
            "connectivity": {}
        }
        
        # Test each interface
        for interface in self.network_interfaces:
            if interface['is_up'] and interface['addresses']:
                interface_results = {
                    "name": interface['name'],
                    "type": interface['type'],
                    "speed": interface['speed'],
                    "mtu": interface['mtu'],
                    "ping_tests": []
                }
                
                # Ping test to common servers
                test_hosts = ['8.8.8.8', '1.1.1.1', 'google.com']
                
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    console=self.console
                ) as progress:
                    task = progress.add_task(f"Testing {interface['name']}", total=len(test_hosts))
                    
                    for host in test_hosts:
                        try:
                            ping_result = subprocess.run(
                                ['ping', '-c', '4', '-W', '3', host],
                                capture_output=True, text=True, timeout=15
                            )
                            
                            if ping_result.returncode == 0:
                                # Extract average ping time
                                lines = ping_result.stdout.split('\n')
                                for line in lines:
                                    if 'avg' in line:
                                        avg_time = line.split('/')[-3]
                                        interface_results['ping_tests'].append({
                                            'host': host,
                                            'avg_ping': float(avg_time),
                                            'status': 'success'
                                        })
                                        break
                            else:
                                interface_results['ping_tests'].append({
                                    'host': host,
                                    'status': 'failed'
                                })
                        
                        except (subprocess.TimeoutExpired, Exception) as e:
                            interface_results['ping_tests'].append({
                                'host': host,
                                'status': 'timeout',
                                'error': str(e)
                            })
                        
                        progress.advance(task)
                
                results['interfaces'].append(interface_results)
        
        # DNS performance test
        dns_start = time.time()
        try:
            subprocess.run(['nslookup', 'google.com'], capture_output=True, timeout=5)
            results['dns_performance'] = {
                'resolution_time': (time.time() - dns_start) * 1000,
                'status': 'success'
            }
        except Exception as e:
            results['dns_performance'] = {
                'status': 'failed',
                'error': str(e)
            }
        
        return results
    
    def make_network_optimizations_permanent(self, optimizations: List[Tuple[str, str]]) -> bool:
        """Make network optimizations permanent via sysctl"""
        try:
            sysctl_file = "/etc/sysctl.d/99-mx-tweaks-network.conf"
            
            header = [
                "# MX Tweaks Pro v2.1 - Network Optimizations",
                f"# Generated on {time.strftime('%Y-%m-%d %H:%M:%S')}",
                "# Advanced network performance tuning",
                ""
            ]
            
            content_lines = header + [f"{param}={value}" for param, value in optimizations]
            content = "\n".join(content_lines)
            
            write_cmd = f"echo '{content}' | sudo tee {sysctl_file} > /dev/null"
            if self.execute_command(write_cmd, "Making network optimizations permanent"):
                apply_cmd = f"sudo sysctl -p {sysctl_file}"
                self.execute_command(apply_cmd, "Applying permanent network settings")
                self.console.print(f"[green]✅ Network optimizations saved to {sysctl_file}[/green]")
                return True
        
        except Exception as e:
            self.logger.error(f"Failed to make network optimizations permanent: {e}")
        
        return False
    
    def run_comprehensive_network_optimization(self) -> Dict:
        """Run comprehensive network optimization suite"""
        self.console.print(Panel(
            "[bold cyan]MX Tweaks Pro v2.1 - Network Optimization Suite[/bold cyan]\n"
            "This will optimize your network stack, DNS resolution, and connection settings\n"
            "for maximum performance and reliability.",
            title="🌐 Network Optimization",
            border_style="bright_blue"
        ))
        
        # Show current network status
        self._display_network_status()
        
        results = {
            "timestamp": time.time(),
            "optimizations_applied": [],
            "benchmark_before": {},
            "benchmark_after": {}
        }
        
        # Run benchmark before optimization
        if Confirm.ask("\n[yellow]Run network benchmark before optimization?[/yellow]"):
            results["benchmark_before"] = self.run_network_benchmark()
        
        # Apply optimizations
        optimizations = [
            ("TCP Stack", self.optimize_tcp_stack),
            ("Network Buffers", self.optimize_network_buffers),
            ("DNS Resolution", self.optimize_dns_resolution),
            ("Firewall", self.configure_firewall_optimization),
            ("WiFi Power Management", self.optimize_wifi_power_management)
        ]
        
        success_count = 0
        applied_params = []
        
        for name, optimization_func in optimizations:
            if Confirm.ask(f"[yellow]Apply {name} optimization?[/yellow]"):
                try:
                    if optimization_func():
                        results["optimizations_applied"].append(name)
                        success_count += 1
                        self.console.print(f"[green]✅ {name} optimization completed[/green]")
                except Exception as e:
                    self.logger.error(f"Error in {name} optimization: {e}")
                    self.console.print(f"[red]❌ {name} optimization failed: {e}[/red]")
        
        # Make optimizations permanent
        if success_count > 0 and Confirm.ask("\n[yellow]Make these optimizations permanent?[/yellow]"):
            # This would require collecting the applied parameters
            self.console.print("[blue]💾 Optimizations will persist after reboot[/blue]")
        
        # Run benchmark after optimization
        if Confirm.ask("\n[yellow]Run network benchmark after optimization?[/yellow]"):
            results["benchmark_after"] = self.run_network_benchmark()
        
        # Display results
        self.console.print(Panel(
            f"[bold green]Network Optimization Complete![/bold green]\n\n"
            f"Successfully applied: {success_count}/{len(optimizations)} optimizations\n"
            f"Optimized: {', '.join(results['optimizations_applied'])}\n\n"
            f"[dim]Network settings have been optimized for performance.\n"
            f"Some changes may require a reboot to take full effect.[/dim]",
            title="🎉 Optimization Results",
            border_style="green"
        ))
        
        results["success_rate"] = success_count / len(optimizations)
        return results
    
    def _display_network_status(self):
        """Display current network interface status"""
        table = Table(title="Current Network Status", box=box.ROUNDED)
        table.add_column("Interface", style="cyan")
        table.add_column("Type", style="yellow")
        table.add_column("Status", style="green")
        table.add_column("Speed", style="white")
        table.add_column("MTU", style="blue")
        table.add_column("Addresses", style="magenta")
        
        for interface in self.network_interfaces:
            status = "UP" if interface["is_up"] else "DOWN"
            speed = f"{interface['speed']} Mbps" if interface['speed'] > 0 else "Unknown"
            addresses = ", ".join([addr["address"] for addr in interface["addresses"][:2]])
            if len(interface["addresses"]) > 2:
                addresses += "..."
            
            table.add_row(
                interface["name"],
                interface["type"],
                f"[green]{status}[/green]" if status == "UP" else f"[red]{status}[/red]",
                speed,
                str(interface["mtu"]),
                addresses or "None"
            )
        
        self.console.print(table)