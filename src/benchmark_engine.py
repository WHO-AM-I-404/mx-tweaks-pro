#!/usr/bin/env python3
"""
Benchmark Engine for MX Tweaks Pro v2.1
Provides comprehensive system benchmarking and performance analysis
"""

import os
import time
import subprocess
import threading
from pathlib import Path
from typing import Dict, List, Tuple
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.table import Table
from rich.panel import Panel
from rich import box
import psutil

class BenchmarkEngine:
    """Advanced system benchmarking engine"""
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.console = Console()
        self.results = {}
    
    def cpu_benchmark(self, duration: int = 10) -> Dict:
        """CPU benchmark using mathematical calculations"""
        self.logger.info("Starting CPU benchmark")
        
        def cpu_stress():
            """CPU stress test function"""
            end_time = time.time() + duration
            operations = 0
            while time.time() < end_time:
                # Mathematical operations to stress CPU
                for i in range(1000):
                    _ = i ** 2 * 3.14159 / 2.71828
                operations += 1000
            return operations
        
        # Get CPU info
        cpu_count = psutil.cpu_count(logical=True)
        initial_cpu = psutil.cpu_percent(interval=1)
        
        # Start benchmark
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeRemainingColumn(),
            console=self.console
        ) as progress:
            task = progress.add_task(f"CPU Benchmark ({cpu_count} threads)", total=duration)
            
            start_time = time.time()
            threads = []
            results = []
            
            # Start worker threads
            for i in range(cpu_count):
                thread = threading.Thread(target=lambda: results.append(cpu_stress()))
                thread.start()
                threads.append(thread)
            
            # Update progress
            while any(t.is_alive() for t in threads):
                elapsed = time.time() - start_time
                progress.update(task, completed=min(elapsed, duration))
                time.sleep(0.1)
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            progress.update(task, completed=duration)
        
        # Calculate results
        total_operations = sum(results) if results else 0
        operations_per_second = total_operations / duration
        final_cpu = psutil.cpu_percent(interval=1)
        
        return {
            "duration": duration,
            "threads_used": cpu_count,
            "total_operations": total_operations,
            "operations_per_second": operations_per_second,
            "initial_cpu_usage": initial_cpu,
            "peak_cpu_usage": final_cpu,
            "score": operations_per_second / 1000  # Normalized score
        }
    
    def memory_benchmark(self, size_mb: int = 512) -> Dict:
        """Memory benchmark testing read/write speeds"""
        self.logger.info(f"Starting memory benchmark ({size_mb}MB)")
        
        # Convert to bytes
        size_bytes = size_mb * 1024 * 1024
        chunk_size = 1024 * 1024  # 1MB chunks
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=self.console
        ) as progress:
            # Write test
            write_task = progress.add_task("Memory Write Test", total=size_mb)
            start_time = time.time()
            
            data = bytearray(size_bytes)
            for i in range(0, size_bytes, chunk_size):
                data[i:i+chunk_size] = b'\x55' * min(chunk_size, size_bytes - i)
                progress.update(write_task, completed=i // (1024*1024))
            
            write_time = time.time() - start_time
            progress.update(write_task, completed=size_mb)
            
            # Read test
            read_task = progress.add_task("Memory Read Test", total=size_mb)
            start_time = time.time()
            
            checksum = 0
            for i in range(0, size_bytes, chunk_size):
                chunk = data[i:i+chunk_size]
                checksum += sum(chunk)
                progress.update(read_task, completed=i // (1024*1024))
            
            read_time = time.time() - start_time
            progress.update(read_task, completed=size_mb)
        
        # Calculate speeds
        write_speed = size_mb / write_time if write_time > 0 else 0
        read_speed = size_mb / read_time if read_time > 0 else 0
        
        return {
            "size_mb": size_mb,
            "write_time": write_time,
            "read_time": read_time,
            "write_speed_mbps": write_speed,
            "read_speed_mbps": read_speed,
            "checksum": checksum,
            "score": (write_speed + read_speed) / 2
        }
    
    def disk_benchmark(self, test_file: str = "/tmp/mx-tweaks-disk-test", size_mb: int = 100) -> Dict:
        """Disk I/O benchmark"""
        self.logger.info(f"Starting disk benchmark ({size_mb}MB)")
        
        test_path = Path(test_file)
        size_bytes = size_mb * 1024 * 1024
        block_size = 1024 * 1024  # 1MB blocks
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                console=self.console
            ) as progress:
                # Write test
                write_task = progress.add_task("Disk Write Test", total=size_mb)
                start_time = time.time()
                
                with open(test_path, 'wb') as f:
                    data_block = b'\x55' * block_size
                    written = 0
                    while written < size_bytes:
                        f.write(data_block)
                        f.flush()
                        os.fsync(f.fileno())  # Force write to disk
                        written += block_size
                        progress.update(write_task, completed=written // (1024*1024))
                
                write_time = time.time() - start_time
                
                # Read test
                read_task = progress.add_task("Disk Read Test", total=size_mb)
                start_time = time.time()
                
                with open(test_path, 'rb') as f:
                    read = 0
                    while read < size_bytes:
                        chunk = f.read(block_size)
                        if not chunk:
                            break
                        read += len(chunk)
                        progress.update(read_task, completed=read // (1024*1024))
                
                read_time = time.time() - start_time
        
        finally:
            # Clean up test file
            try:
                test_path.unlink()
            except:
                pass
        
        # Calculate speeds
        write_speed = size_mb / write_time if write_time > 0 else 0
        read_speed = size_mb / read_time if read_time > 0 else 0
        
        return {
            "size_mb": size_mb,
            "write_time": write_time,
            "read_time": read_time,
            "write_speed_mbps": write_speed,
            "read_speed_mbps": read_speed,
            "score": (write_speed + read_speed) / 2
        }
    
    def network_benchmark(self) -> Dict:
        """Network interface benchmark"""
        self.logger.info("Starting network benchmark")
        
        try:
            # Get initial network stats
            initial_stats = psutil.net_io_counters()
            time.sleep(2)
            final_stats = psutil.net_io_counters()
            
            # Calculate throughput
            bytes_sent = final_stats.bytes_sent - initial_stats.bytes_sent
            bytes_recv = final_stats.bytes_recv - initial_stats.bytes_recv
            packets_sent = final_stats.packets_sent - initial_stats.packets_sent
            packets_recv = final_stats.packets_recv - initial_stats.packets_recv
            
            # Get interface speeds
            interfaces = psutil.net_if_stats()
            max_speed = 0
            active_interfaces = []
            
            for name, stats in interfaces.items():
                if stats.isup and stats.speed > 0:
                    max_speed = max(max_speed, stats.speed)
                    active_interfaces.append({
                        "name": name,
                        "speed_mbps": stats.speed,
                        "mtu": stats.mtu
                    })
            
            return {
                "duration": 2,
                "bytes_sent": bytes_sent,
                "bytes_received": bytes_recv,
                "packets_sent": packets_sent,
                "packets_received": packets_recv,
                "max_interface_speed": max_speed,
                "active_interfaces": active_interfaces,
                "throughput_mbps": (bytes_sent + bytes_recv) * 8 / (2 * 1024 * 1024)
            }
        
        except Exception as e:
            self.logger.error(f"Network benchmark error: {e}")
            return {"error": str(e)}
    
    def system_stress_test(self, duration: int = 30) -> Dict:
        """Comprehensive system stress test"""
        self.logger.info(f"Starting system stress test ({duration}s)")
        
        # Monitor system during stress
        cpu_samples = []
        memory_samples = []
        temp_samples = []
        
        def monitor_system():
            """System monitoring thread"""
            end_time = time.time() + duration
            while time.time() < end_time:
                cpu_samples.append(psutil.cpu_percent())
                memory_samples.append(psutil.virtual_memory().percent)
                
                # Try to get temperature
                try:
                    temps = psutil.sensors_temperatures()
                    if temps:
                        for name, entries in temps.items():
                            for entry in entries:
                                if entry.current:
                                    temp_samples.append(entry.current)
                                    break
                            break
                except:
                    pass
                
                time.sleep(1)
        
        # Start monitoring
        monitor_thread = threading.Thread(target=monitor_system)
        monitor_thread.start()
        
        # Run mini benchmarks
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("System Stress Test", total=3)
            
            cpu_result = self.cpu_benchmark(duration // 3)
            progress.advance(task)
            
            memory_result = self.memory_benchmark(128)
            progress.advance(task)
            
            disk_result = self.disk_benchmark(size_mb=50)
            progress.advance(task)
        
        # Wait for monitoring to finish
        monitor_thread.join()
        
        # Calculate statistics
        avg_cpu = sum(cpu_samples) / len(cpu_samples) if cpu_samples else 0
        max_cpu = max(cpu_samples) if cpu_samples else 0
        avg_memory = sum(memory_samples) / len(memory_samples) if memory_samples else 0
        max_memory = max(memory_samples) if memory_samples else 0
        avg_temp = sum(temp_samples) / len(temp_samples) if temp_samples else 0
        max_temp = max(temp_samples) if temp_samples else 0
        
        return {
            "duration": duration,
            "cpu_performance": cpu_result["score"],
            "memory_performance": memory_result["score"],
            "disk_performance": disk_result["score"],
            "average_cpu_usage": avg_cpu,
            "peak_cpu_usage": max_cpu,
            "average_memory_usage": avg_memory,
            "peak_memory_usage": max_memory,
            "average_temperature": avg_temp,
            "peak_temperature": max_temp,
            "stability_score": 100 - (max_cpu + max_memory) / 2
        }
    
    def run_full_benchmark(self) -> Dict:
        """Run complete system benchmark suite"""
        self.console.print(Panel(
            "[bold cyan]MX Tweaks Pro v2.1 - System Benchmark Suite[/bold cyan]\n"
            "This will test your system's CPU, Memory, Disk, and Network performance.\n"
            "The benchmark may take several minutes to complete.",
            title="🚀 Benchmark Starting",
            border_style="bright_blue"
        ))
        
        results = {
            "timestamp": time.time(),
            "system_info": {
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "platform": os.uname()
            }
        }
        
        try:
            # CPU Benchmark
            self.console.print("\n[bold yellow]🔧 CPU Performance Test[/bold yellow]")
            results["cpu"] = self.cpu_benchmark(15)
            
            # Memory Benchmark
            self.console.print("\n[bold yellow]💾 Memory Performance Test[/bold yellow]")
            results["memory"] = self.memory_benchmark(256)
            
            # Disk Benchmark
            self.console.print("\n[bold yellow]💿 Disk I/O Performance Test[/bold yellow]")
            results["disk"] = self.disk_benchmark(size_mb=200)
            
            # Network Benchmark
            self.console.print("\n[bold yellow]🌐 Network Interface Test[/bold yellow]")
            results["network"] = self.network_benchmark()
            
            # System Stress Test
            self.console.print("\n[bold yellow]⚡ System Stress Test[/bold yellow]")
            results["stress_test"] = self.system_stress_test(45)
            
            # Calculate overall score
            cpu_score = results["cpu"]["score"]
            memory_score = results["memory"]["score"]
            disk_score = results["disk"]["score"]
            stability_score = results["stress_test"]["stability_score"]
            
            overall_score = (cpu_score + memory_score + disk_score + stability_score) / 4
            results["overall_score"] = overall_score
            
            # Display results
            self.display_benchmark_results(results)
            
            # Save results
            self.save_benchmark_results(results)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Benchmark error: {e}")
            self.console.print(f"[red]❌ Benchmark failed: {e}[/red]")
            return {"error": str(e)}
    
    def display_benchmark_results(self, results: Dict):
        """Display comprehensive benchmark results"""
        self.console.print("\n" + "="*60)
        self.console.print("[bold green]🏆 BENCHMARK RESULTS[/bold green]")
        self.console.print("="*60)
        
        # Overall Score
        overall_score = results.get("overall_score", 0)
        score_color = "green" if overall_score > 75 else "yellow" if overall_score > 50 else "red"
        
        self.console.print(f"\n[bold {score_color}]Overall Performance Score: {overall_score:.1f}/100[/bold {score_color}]")
        
        # Detailed Results Table
        table = Table(title="📊 Detailed Performance Results", box=box.ROUNDED)
        table.add_column("Component", style="cyan", width=15)
        table.add_column("Metric", style="white", width=25)
        table.add_column("Value", style="green", width=20)
        table.add_column("Score", style="yellow", width=10)
        
        # CPU Results
        if "cpu" in results:
            cpu = results["cpu"]
            table.add_row("CPU", "Operations/Second", f"{cpu['operations_per_second']:.0f}", f"{cpu['score']:.1f}")
            table.add_row("", "Peak Usage", f"{cpu['peak_cpu_usage']:.1f}%", "")
        
        # Memory Results
        if "memory" in results:
            memory = results["memory"]
            table.add_row("Memory", "Read Speed", f"{memory['read_speed_mbps']:.1f} MB/s", f"{memory['score']:.1f}")
            table.add_row("", "Write Speed", f"{memory['write_speed_mbps']:.1f} MB/s", "")
        
        # Disk Results
        if "disk" in results:
            disk = results["disk"]
            table.add_row("Disk I/O", "Read Speed", f"{disk['read_speed_mbps']:.1f} MB/s", f"{disk['score']:.1f}")
            table.add_row("", "Write Speed", f"{disk['write_speed_mbps']:.1f} MB/s", "")
        
        # Stress Test Results
        if "stress_test" in results:
            stress = results["stress_test"]
            table.add_row("Stability", "Average CPU", f"{stress['average_cpu_usage']:.1f}%", f"{stress['stability_score']:.1f}")
            table.add_row("", "Peak Memory", f"{stress['peak_memory_usage']:.1f}%", "")
            if stress["peak_temperature"] > 0:
                table.add_row("", "Peak Temperature", f"{stress['peak_temperature']:.1f}°C", "")
        
        self.console.print(table)
        
        # Performance Rating
        if overall_score > 90:
            rating = "[bold green]🚀 Excellent - Your system is running at peak performance![/bold green]"
        elif overall_score > 75:
            rating = "[bold yellow]⚡ Good - Your system performs well with room for optimization.[/bold yellow]"
        elif overall_score > 50:
            rating = "[bold orange]⚠️  Average - Consider system optimization to improve performance.[/bold orange]"
        else:
            rating = "[bold red]🐌 Poor - Your system needs significant optimization.[/bold red]"
        
        self.console.print(f"\n{rating}")
    
    def save_benchmark_results(self, results: Dict):
        """Save benchmark results to file"""
        try:
            config_dir = Path.home() / '.config' / 'mx-tweaks-pro' / 'benchmarks'
            config_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = config_dir / f"benchmark_{timestamp}.json"
            
            import json
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            self.console.print(f"\n[dim]📁 Results saved to: {filename}[/dim]")
            
        except Exception as e:
            self.logger.error(f"Failed to save benchmark results: {e}")