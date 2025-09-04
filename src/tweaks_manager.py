#!/usr/bin/env python3
"""
Tweaks Manager - Mengelola berbagai tweaks sistem untuk MX Linux
"""

import os
import subprocess
import psutil
import shutil
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.prompt import Confirm

class TweaksManager:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.console = Console()
        
    def run_command(self, command, description="Menjalankan perintah"):
        """Menjalankan command dengan progress indicator yang keren"""
        try:
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
                    check=True
                )
                
                progress.update(task, completed=100)
                
            if result.returncode == 0:
                self.console.print(f"[green]✅ {description} berhasil![/green]")
                self.logger.info(f"Command berhasil: {command}")
                return True
            else:
                self.console.print(f"[red]❌ {description} gagal![/red]")
                self.logger.error(f"Command gagal: {command} - {result.stderr}")
                return False
                
        except subprocess.CalledProcessError as e:
            self.console.print(f"[red]❌ {description} gagal: {e.stderr}[/red]")
            self.logger.error(f"Command error: {command} - {e.stderr}")
            return False
        except Exception as e:
            self.console.print(f"[red]❌ Error tidak terduga: {e}[/red]")
            self.logger.error(f"Unexpected error: {e}")
            return False
    
    def disable_swap(self):
        """Menonaktifkan swap untuk optimasi SSD"""
        self.console.print("\n[bold cyan]🚀 MENONAKTIFKAN SWAP[/bold cyan]")
        
        # Cek apakah swap sedang aktif
        swap_info = psutil.swap_memory()
        if swap_info.total == 0:
            self.console.print("[yellow]ℹ️  Swap sudah tidak aktif.[/yellow]")
            return
        
        # Konfirmasi dari user
        if not Confirm.ask(
            "\n[yellow]⚠️  Menonaktifkan swap dapat mempengaruhi performa jika RAM penuh.\n"
            "Apakah Anda yakin ingin melanjutkan?[/yellow]"
        ):
            return
        
        # Nonaktifkan swap
        if self.run_command("sudo swapoff -a", "Menonaktifkan swap"):
            # Backup fstab
            if self.run_command("sudo cp /etc/fstab /etc/fstab.backup", "Backup fstab"):
                # Comment swap entries di fstab
                if self.run_command(
                    "sudo sed -i '/ swap / s/^/#/' /etc/fstab", 
                    "Update konfigurasi fstab"
                ):
                    self.console.print("\n[bold green]🎉 Swap berhasil dinonaktifkan![/bold green]")
                    self.console.print("[dim]Perubahan akan permanen setelah reboot.[/dim]")
    
    def clean_package_cache(self):
        """Membersihkan cache package manager"""
        self.console.print("\n[bold cyan]📦 MEMBERSIHKAN PACKAGE CACHE[/bold cyan]")
        
        # Cek ukuran cache sebelum dibersihkan
        cache_paths = [
            "/var/cache/apt/archives",
            "/var/cache/apt/archives/partial"
        ]
        
        total_size = 0
        for path in cache_paths:
            if os.path.exists(path):
                for root, dirs, files in os.walk(path):
                    total_size += sum(os.path.getsize(os.path.join(root, file)) for file in files)
        
        size_mb = total_size / (1024 * 1024)
        self.console.print(f"[yellow]📊 Ukuran cache saat ini: {size_mb:.1f} MB[/yellow]")
        
        if size_mb < 1:
            self.console.print("[green]✅ Cache sudah bersih![/green]")
            return
        
        # Bersihkan cache
        if self.run_command("sudo apt-get clean", "Membersihkan APT cache"):
            if self.run_command("sudo apt-get autoclean", "Membersihkan cache lama"):
                self.console.print(f"\n[bold green]🎉 Cache berhasil dibersihkan! (Menghemat {size_mb:.1f} MB)[/bold green]")
    
    def clean_temp_files(self):
        """Membersihkan file temporary"""
        self.console.print("\n[bold cyan]🗑️  MEMBERSIHKAN FILE TEMPORARY[/bold cyan]")
        
        temp_paths = [
            "/tmp/*",
            "/var/tmp/*",
            "~/.cache/thumbnails/*",
            "~/.local/share/Trash/*"
        ]
        
        cleaned_count = 0
        for path in temp_paths:
            if self.run_command(f"sudo find {path} -type f -mtime +7 -delete 2>/dev/null || true", 
                               f"Membersihkan {path}"):
                cleaned_count += 1
        
        if cleaned_count > 0:
            self.console.print("\n[bold green]🎉 File temporary berhasil dibersihkan![/bold green]")
    
    def optimize_boot_time(self):
        """Optimasi waktu boot sistem"""
        self.console.print("\n[bold cyan]⚡ OPTIMASI BOOT TIME[/bold cyan]")
        
        # Analisa boot time saat ini
        if self.run_command("systemd-analyze", "Menganalisa boot time"):
            # Disable beberapa service yang tidak perlu
            services_to_disable = [
                "bluetooth.service",
                "cups.service", 
                "ModemManager.service"
            ]
            
            disabled_services = []
            for service in services_to_disable:
                # Cek apakah service aktif
                result = subprocess.run(
                    f"systemctl is-enabled {service} 2>/dev/null",
                    shell=True, capture_output=True, text=True
                )
                
                if result.returncode == 0 and "enabled" in result.stdout:
                    if Confirm.ask(f"\n[yellow]Nonaktifkan {service}? (dapat diaktifkan kembali nanti)[/yellow]"):
                        if self.run_command(f"sudo systemctl disable {service}", f"Menonaktifkan {service}"):
                            disabled_services.append(service)
            
            if disabled_services:
                self.console.print(f"\n[bold green]🎉 Boot time optimasi selesai![/bold green]")
                self.console.print(f"[dim]Service yang dinonaktifkan: {', '.join(disabled_services)}[/dim]")
            else:
                self.console.print("[yellow]ℹ️  Tidak ada service yang perlu dinonaktifkan.[/yellow]")
    
    def fix_broken_packages(self):
        """Memperbaiki package yang rusak"""
        self.console.print("\n[bold cyan]🔧 MEMPERBAIKI BROKEN PACKAGES[/bold cyan]")
        
        commands = [
            ("sudo apt-get update", "Update package list"),
            ("sudo apt-get -f install", "Fix broken dependencies"),
            ("sudo dpkg --configure -a", "Configure pending packages"),
            ("sudo apt-get autoremove", "Remove unnecessary packages")
        ]
        
        success_count = 0
        for command, description in commands:
            if self.run_command(command, description):
                success_count += 1
        
        if success_count == len(commands):
            self.console.print("\n[bold green]🎉 Semua package berhasil diperbaiki![/bold green]")
        else:
            self.console.print("\n[yellow]⚠️  Beberapa perintah mungkin gagal, cek log untuk detail.[/yellow]")
    
    def optimize_cpu_governor(self):
        """Optimasi CPU governor untuk performa"""
        self.console.print("\n[bold cyan]🎯 OPTIMASI CPU GOVERNOR[/bold cyan]")
        
        # Cek governor saat ini
        try:
            with open('/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor', 'r') as f:
                current_governor = f.read().strip()
            
            self.console.print(f"[yellow]📊 Governor saat ini: {current_governor}[/yellow]")
            
            # Set ke performance governor
            if current_governor != "performance":
                if Confirm.ask("\n[yellow]Ganti ke 'performance' governor untuk performa maksimal?[/yellow]"):
                    if self.run_command(
                        "echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor",
                        "Set performance governor"
                    ):
                        self.console.print("\n[bold green]🎉 CPU governor berhasil dioptimasi![/bold green]")
                        self.console.print("[dim]Perubahan akan hilang setelah reboot kecuali dikonfigurasi permanent.[/dim]")
            else:
                self.console.print("[green]✅ CPU governor sudah optimal![/green]")
                
        except FileNotFoundError:
            self.console.print("[red]❌ CPU frequency scaling tidak tersedia pada sistem ini.[/red]")
    
    def tune_memory(self):
        """Tuning parameter memory"""
        self.console.print("\n[bold cyan]💾 TUNING MEMORY[/bold cyan]")
        
        # Set swappiness ke nilai optimal
        if self.run_command("echo 10 | sudo tee /proc/sys/vm/swappiness", "Set swappiness ke 10"):
            # Set dirty ratio untuk I/O performance
            if self.run_command("echo 15 | sudo tee /proc/sys/vm/dirty_ratio", "Set dirty ratio ke 15"):
                self.console.print("\n[bold green]🎉 Memory tuning selesai![/bold green]")
                self.console.print("[dim]Perubahan akan hilang setelah reboot kecuali dikonfigurasi di sysctl.[/dim]")
    
    def disable_unnecessary_services(self):
        """Nonaktifkan service yang tidak perlu"""
        self.console.print("\n[bold cyan]🔥 DISABLE UNNECESSARY SERVICES[/bold cyan]")
        
        # Service yang biasanya tidak diperlukan
        services = {
            "bluetooth.service": "Bluetooth support",
            "cups.service": "Printing service",
            "ModemManager.service": "Modem management",
            "whoopsie.service": "Ubuntu error reporting",
            "apport.service": "Automatic crash reporting"
        }
        
        disabled_count = 0
        for service, description in services.items():
            # Cek apakah service ada dan aktif
            result = subprocess.run(
                f"systemctl is-active {service} 2>/dev/null",
                shell=True, capture_output=True, text=True
            )
            
            if result.returncode == 0 and "active" in result.stdout:
                if Confirm.ask(f"\n[yellow]Nonaktifkan {service}? ({description})[/yellow]"):
                    if self.run_command(f"sudo systemctl disable {service}", f"Disable {service}"):
                        if self.run_command(f"sudo systemctl stop {service}", f"Stop {service}"):
                            disabled_count += 1
        
        if disabled_count > 0:
            self.console.print(f"\n[bold green]🎉 {disabled_count} service berhasil dinonaktifkan![/bold green]")
        else:
            self.console.print("[yellow]ℹ️  Tidak ada service yang perlu dinonaktifkan.[/yellow]")
    
    def optimize_io_scheduler(self):
        """Optimasi I/O scheduler"""
        self.console.print("\n[bold cyan]⚡ I/O SCHEDULER OPTIMIZATION[/bold cyan]")
        
        # Deteksi tipe disk (SSD/HDD)
        disks = psutil.disk_partitions()
        for disk in disks:
            if disk.device.startswith('/dev/sd') or disk.device.startswith('/dev/nvme'):
                device_name = disk.device.split('/')[-1].rstrip('0123456789')
                
                # Cek apakah SSD
                rotational_file = f"/sys/block/{device_name}/queue/rotational"
                try:
                    with open(rotational_file, 'r') as f:
                        is_ssd = f.read().strip() == '0'
                    
                    scheduler = "mq-deadline" if is_ssd else "bfq"
                    scheduler_file = f"/sys/block/{device_name}/queue/scheduler"
                    
                    if self.run_command(
                        f"echo {scheduler} | sudo tee {scheduler_file}",
                        f"Set {scheduler} scheduler untuk {device_name}"
                    ):
                        disk_type = "SSD" if is_ssd else "HDD"
                        self.console.print(f"[green]✅ {device_name} ({disk_type}) - scheduler set ke {scheduler}[/green]")
                        
                except FileNotFoundError:
                    continue
        
        self.console.print("\n[bold green]🎉 I/O scheduler optimization selesai![/bold green]")
    
    def optimize_preload(self):
        """Optimasi preload untuk aplikasi yang sering digunakan"""
        self.console.print("\n[bold cyan]🚀 PRELOAD OPTIMIZATION[/bold cyan]")
        
        # Install preload jika belum ada
        result = subprocess.run("which preload", shell=True, capture_output=True)
        if result.returncode != 0:
            if Confirm.ask("\n[yellow]Install preload untuk mempercepat loading aplikasi?[/yellow]"):
                if self.run_command("sudo apt-get install -y preload", "Install preload"):
                    if self.run_command("sudo systemctl enable preload", "Enable preload service"):
                        if self.run_command("sudo systemctl start preload", "Start preload service"):
                            self.console.print("\n[bold green]🎉 Preload berhasil diinstall dan diaktifkan![/bold green]")
                            self.console.print("[dim]Preload akan mempelajari pola penggunaan aplikasi Anda.[/dim]")
        else:
            self.console.print("[green]✅ Preload sudah terinstall![/green]")
            # Restart preload untuk refresh
            if self.run_command("sudo systemctl restart preload", "Restart preload service"):
                self.console.print("[green]✅ Preload service di-restart![/green]")
    
    def get_system_info(self):
        """Mengumpulkan informasi sistem lengkap"""
        info = {
            'cpu': {},
            'memory': {},
            'disk': []
        }
        
        # CPU Info
        info['cpu'] = {
            'Model': psutil.cpu_count(logical=False),
            'Logical Cores': psutil.cpu_count(logical=True),
            'Max Frequency': f"{psutil.cpu_freq().max:.0f} MHz" if psutil.cpu_freq() else "Unknown",
            'Current Usage': f"{psutil.cpu_percent(interval=1):.1f}%"
        }
        
        # Memory Info
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        info['memory'] = {
            'Total RAM': f"{memory.total / (1024**3):.1f} GB",
            'Available RAM': f"{memory.available / (1024**3):.1f} GB",
            'Used RAM': f"{memory.used / (1024**3):.1f} GB",
            'RAM Usage': f"{memory.percent:.1f}%",
            'Total Swap': f"{swap.total / (1024**3):.1f} GB" if swap.total > 0 else "Disabled",
            'Swap Usage': f"{swap.percent:.1f}%" if swap.total > 0 else "N/A"
        }
        
        # Disk Info
        partitions = psutil.disk_partitions()
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                info['disk'].append({
                    'device': partition.device,
                    'size': f"{usage.total / (1024**3):.1f} GB",
                    'used': f"{usage.used / (1024**3):.1f} GB",
                    'free': f"{usage.free / (1024**3):.1f} GB",
                    'usage': f"{usage.percent:.1f}%"
                })
            except PermissionError:
                continue
        
        return info