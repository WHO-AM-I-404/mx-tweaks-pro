#!/usr/bin/env python3
"""
CLI Interface untuk MX Tweaks Pro
Menggunakan Rich library untuk tampilan terminal yang keren
"""

import os
import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.align import Align
from rich import box
from rich.columns import Columns

from .tweaks_manager import TweaksManager
from .backup_manager import BackupManager

class CLIInterface:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.console = Console()
        self.tweaks = TweaksManager(config, logger)
        self.backup = BackupManager(config, logger)
        
    def show_banner(self):
        """Tampilkan banner aplikasi yang keren"""
        banner_text = Text()
        banner_text.append("███╗   ███╗██╗  ██╗    ", style="bold cyan")
        banner_text.append("████╗ ████║╚██╗██╔╝    ", style="bold cyan")
        banner_text.append("██╔████╔██║ ╚███╔╝     ", style="bold cyan")
        banner_text.append("██║╚██╔╝██║ ██╔██╗     ", style="bold cyan")
        banner_text.append("██║ ╚═╝ ██║██╔╝ ██╗    ", style="bold cyan")
        banner_text.append("╚═╝     ╚═╝╚═╝  ╚═╝    ", style="bold cyan")
        banner_text.append("\n")
        banner_text.append("TWEAKS PRO", style="bold magenta")
        
        subtitle = Text("🚀 Utility Tweaking Canggih untuk MX Linux", style="bold white")
        version = Text("v1.0.0 - Dibuat dengan ❤️ untuk komunitas MX Linux", style="dim")
        
        banner_panel = Panel(
            Align.center(banner_text + "\n" + subtitle + "\n" + version),
            box=box.DOUBLE,
            border_style="bright_blue",
            padding=(1, 2)
        )
        
        self.console.print(banner_panel)
        self.console.print()
    
    def show_main_menu(self):
        """Tampilkan menu utama dengan style yang keren"""
        table = Table(show_header=False, box=box.ROUNDED, border_style="bright_green")
        table.add_column("No", style="bold cyan", width=4)
        table.add_column("Menu", style="bold white", width=35)
        table.add_column("Deskripsi", style="dim white")
        
        menu_items = [
            ("1", "🔧 System Tweaks", "Optimasi sistem dan performa"),
            ("2", "🎨 Appearance Tweaks", "Kustomisasi tampilan desktop"),
            ("3", "🌐 Network Tweaks", "Optimasi koneksi internet"),
            ("4", "⚡ Performance Tweaks", "Boost performa sistem"),
            ("5", "🛡️ Security Tweaks", "Pengaturan keamanan sistem"),
            ("6", "💾 Backup & Restore", "Kelola backup konfigurasi"),
            ("7", "⚙️ Advanced Settings", "Pengaturan lanjutan"),
            ("8", "📊 System Info", "Informasi sistem lengkap"),
            ("0", "🚪 Keluar", "Keluar dari aplikasi")
        ]
        
        for no, menu, desc in menu_items:
            table.add_row(no, menu, desc)
        
        panel = Panel(
            table,
            title="[bold yellow]🏠 MENU UTAMA MX TWEAKS PRO[/bold yellow]",
            border_style="bright_yellow",
            padding=(1, 2)
        )
        
        self.console.print(panel)
    
    def show_system_tweaks_menu(self):
        """Menu untuk system tweaks"""
        self.console.clear()
        self.console.print("[bold cyan]🔧 SYSTEM TWEAKS[/bold cyan]\n")
        
        table = Table(show_header=False, box=box.ROUNDED)
        table.add_column("No", style="bold cyan", width=4)
        table.add_column("Tweak", style="bold white", width=40)
        table.add_column("Status", style="bold green", width=15)
        
        tweaks = [
            ("1", "🚀 Nonaktifkan Swap (untuk SSD)", "Siap"),
            ("2", "📦 Bersihkan Package Cache", "Siap"),
            ("3", "🗑️ Hapus File Temporary", "Siap"),
            ("4", "⚡ Optimasi Boot Time", "Siap"),
            ("5", "🔧 Fix Broken Packages", "Siap"),
            ("0", "🔙 Kembali ke Menu Utama", "")
        ]
        
        for no, tweak, status in tweaks:
            table.add_row(no, tweak, status)
        
        self.console.print(table)
        
        choice = Prompt.ask("\n[bold yellow]Pilih tweak yang ingin dijalankan[/bold yellow]", 
                          choices=["0", "1", "2", "3", "4", "5"])
        
        if choice == "0":
            return
        elif choice == "1":
            self.tweaks.disable_swap()
        elif choice == "2":
            self.tweaks.clean_package_cache()
        elif choice == "3":
            self.tweaks.clean_temp_files()
        elif choice == "4":
            self.tweaks.optimize_boot_time()
        elif choice == "5":
            self.tweaks.fix_broken_packages()
        
        Prompt.ask("\n[dim]Tekan Enter untuk melanjutkan...[/dim]")
    
    def show_performance_tweaks_menu(self):
        """Menu untuk performance tweaks"""
        self.console.clear()
        self.console.print("[bold magenta]⚡ PERFORMANCE TWEAKS[/bold magenta]\n")
        
        table = Table(show_header=False, box=box.ROUNDED)
        table.add_column("No", style="bold cyan", width=4)
        table.add_column("Tweak", style="bold white", width=40)
        table.add_column("Impact", style="bold yellow", width=15)
        
        tweaks = [
            ("1", "🎯 Optimasi CPU Governor", "Tinggi"),
            ("2", "💾 Tuning Memory", "Sedang"),
            ("3", "🔥 Disable Unnecessary Services", "Tinggi"),
            ("4", "⚡ I/O Scheduler Optimization", "Sedang"),
            ("5", "🚀 Preload Optimization", "Sedang"),
            ("0", "🔙 Kembali ke Menu Utama", "")
        ]
        
        for no, tweak, impact in tweaks:
            table.add_row(no, tweak, impact)
        
        self.console.print(table)
        
        choice = Prompt.ask("\n[bold yellow]Pilih optimasi yang ingin diterapkan[/bold yellow]", 
                          choices=["0", "1", "2", "3", "4", "5"])
        
        if choice == "0":
            return
        elif choice == "1":
            self.tweaks.optimize_cpu_governor()
        elif choice == "2":
            self.tweaks.tune_memory()
        elif choice == "3":
            self.tweaks.disable_unnecessary_services()
        elif choice == "4":
            self.tweaks.optimize_io_scheduler()
        elif choice == "5":
            self.tweaks.optimize_preload()
        
        Prompt.ask("\n[dim]Tekan Enter untuk melanjutkan...[/dim]")
    
    def show_system_info(self):
        """Tampilkan informasi sistem yang detail"""
        self.console.clear()
        
        with self.console.status("[bold green]Mengumpulkan informasi sistem..."):
            info = self.tweaks.get_system_info()
        
        # CPU Info
        cpu_table = Table(title="🖥️ Informasi CPU", box=box.ROUNDED)
        cpu_table.add_column("Property", style="cyan")
        cpu_table.add_column("Value", style="white")
        
        for key, value in info['cpu'].items():
            cpu_table.add_row(key, str(value))
        
        # Memory Info
        mem_table = Table(title="💾 Informasi Memory", box=box.ROUNDED)
        mem_table.add_column("Property", style="cyan")
        mem_table.add_column("Value", style="white")
        
        for key, value in info['memory'].items():
            mem_table.add_row(key, value)
        
        # Disk Info
        disk_table = Table(title="💿 Informasi Disk", box=box.ROUNDED)
        disk_table.add_column("Device", style="cyan")
        disk_table.add_column("Size", style="white")
        disk_table.add_column("Used", style="yellow")
        disk_table.add_column("Free", style="green")
        disk_table.add_column("Usage", style="red")
        
        for disk in info['disk']:
            disk_table.add_row(
                disk['device'], 
                disk['size'], 
                disk['used'], 
                disk['free'], 
                disk['usage']
            )
        
        # Tampilkan dalam kolom
        self.console.print(Columns([cpu_table, mem_table], equal=True))
        self.console.print()
        self.console.print(disk_table)
        
        Prompt.ask("\n[dim]Tekan Enter untuk kembali...[/dim]")
    
    def run(self):
        """Jalankan interface CLI utama"""
        while True:
            self.console.clear()
            self.show_banner()
            self.show_main_menu()
            
            choice = Prompt.ask("\n[bold yellow]Pilih menu[/bold yellow]", 
                              choices=["0", "1", "2", "3", "4", "5", "6", "7", "8"])
            
            if choice == "0":
                self.console.print("\n[bold green]👋 Terima kasih telah menggunakan MX Tweaks Pro![/bold green]")
                break
            elif choice == "1":
                self.show_system_tweaks_menu()
            elif choice == "2":
                self.console.print("\n[yellow]🚧 Appearance Tweaks sedang dalam pengembangan...[/yellow]")
                Prompt.ask("[dim]Tekan Enter untuk melanjutkan...[/dim]")
            elif choice == "3":
                self.console.print("\n[yellow]🚧 Network Tweaks sedang dalam pengembangan...[/yellow]")
                Prompt.ask("[dim]Tekan Enter untuk melanjutkan...[/dim]")
            elif choice == "4":
                self.show_performance_tweaks_menu()
            elif choice == "5":
                self.console.print("\n[yellow]🚧 Security Tweaks sedang dalam pengembangan...[/yellow]")
                Prompt.ask("[dim]Tekan Enter untuk melanjutkan...[/dim]")
            elif choice == "6":
                self.console.print("\n[yellow]🚧 Backup & Restore sedang dalam pengembangan...[/yellow]")
                Prompt.ask("[dim]Tekan Enter untuk melanjutkan...[/dim]")
            elif choice == "7":
                self.console.print("\n[yellow]🚧 Advanced Settings sedang dalam pengembangan...[/yellow]")
                Prompt.ask("[dim]Tekan Enter untuk melanjutkan...[/dim]")
            elif choice == "8":
                self.show_system_info()