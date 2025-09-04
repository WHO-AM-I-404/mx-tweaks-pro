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
    def __init__(self, config, logger, profiler=None):
        self.config = config
        self.logger = logger
        self.console = Console()
        self.tweaks = TweaksManager(config, logger)
        self.backup = BackupManager(config, logger)
        self.profiler = profiler
        
        # Initialize root status info
        self.is_root = self.config.check_root_access()
        
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
        version = Text("v2.1.0 - Advanced System Optimization with Root Access Management", style="dim")
        root_status = Text(f"🔒 {'Root Access: ENABLED' if self.is_root else 'User Mode: Limited Access'}", 
                         style="bold green" if self.is_root else "bold yellow")
        
        banner_panel = Panel(
            Align.center(banner_text + "\n" + subtitle + "\n" + version + "\n" + root_status),
            box=box.DOUBLE,
            border_style="bright_blue",
            padding=(1, 2)
        )
        
        self.console.print(banner_panel)
        self.console.print()
    
    def show_root_status_info(self):
        """Show detailed root status information"""
        if self.is_root:
            self.console.print("[bold green]✅ Running with root privileges - All features available[/bold green]")
        else:
            self.console.print("[bold yellow]⚠️ Running in user mode - Some features require root access[/bold yellow]")
            self.console.print("[dim]Use 'sudo mx-tweaks-pro' for full system optimization features[/dim]")
    
    def check_and_handle_root_requirement(self, operation_name: str, operation_type: str = "system_operation") -> bool:
        """
        Check if operation requires root and handle accordingly
        Returns True if operation can proceed, False otherwise
        """
        if not self.config.check_operation_permissions(operation_type):
            return False
        return True
    
    def show_access_denied_message(self, feature_name: str):
        """Show access denied message for root-required features"""
        self.console.print(Panel(
            f"[bold red]❌ Access Denied[/bold red]\n\n"
            f"[yellow]{feature_name}[/yellow] requires root access.\n\n"
            f"[cyan]Options:[/cyan]\n"
            f"• Exit and run: [green]sudo mx-tweaks-pro[/green]\n"
            f"• Use: [green]pkexec mx-tweaks-pro --gui[/green] for GUI mode\n"
            f"• Continue with user-level features only",
            title="🔒 Root Required",
            border_style="red"
        ))
        return Confirm.ask("Continue with limited functionality?")
    
    def show_main_menu(self):
        """Tampilkan menu utama dengan style yang keren"""
        # Show root status info
        self.show_root_status_info()
        self.console.print()
        
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
    
    def run(self):
        """Main run method for CLI interface"""
        try:
            self.start()
        except Exception as e:
            self.logger.error(f"CLI Interface error: {e}")
            self.console.print(f"[red]❌ Error: {e}[/red]")
            raise
    
    def start(self):
        """Start the CLI interface (kept for backward compatibility)"""
        self.console.clear()
        self.show_banner()
        
        while True:
            self.show_main_menu()
            choice = Prompt.ask("Select an option", default="0")
            
            if choice == "0":
                self.console.print("[yellow]👋 Goodbye! Thank you for using MX Tweaks Pro v2.1[/yellow]")
                break
            elif choice == "1":
                if self.check_and_handle_root_requirement("System Tweaks", "system_cleanup"):
                    self.handle_system_tweaks()
                else:
                    if not self.show_access_denied_message("System Tweaks"):
                        continue
            elif choice == "2":
                self.handle_appearance_tweaks()
            elif choice == "3":
                if self.check_and_handle_root_requirement("Network Tweaks", "network_optimization"):
                    self.handle_network_tweaks()
                else:
                    if not self.show_access_denied_message("Network Tweaks"):
                        continue
            elif choice == "4":
                if self.check_and_handle_root_requirement("Performance Tweaks", "performance_tweaks"):
                    self.handle_performance_tweaks()
                else:
                    if not self.show_access_denied_message("Performance Tweaks"):
                        continue
            elif choice == "5":
                if self.check_and_handle_root_requirement("Security Tweaks", "security_hardening"):
                    self.handle_security_tweaks()
                else:
                    if not self.show_access_denied_message("Security Tweaks"):
                        continue
            elif choice == "6":
                self.handle_backup_restore()
            elif choice == "7":
                self.handle_plugin_system()
            elif choice == "8":
                self.show_system_info()
            elif choice == "9":
                self.handle_settings()
            else:
                self.console.print("[red]❌ Invalid choice. Please try again.[/red]")
                self.console.input("\nPress Enter to continue...")
    
    def handle_system_tweaks(self):
        """Handle system tweaks menu"""
        self.show_system_tweaks_menu()
    
    def handle_appearance_tweaks(self):
        """Handle appearance tweaks (user level)"""
        self.console.print("[green]✅ Appearance Tweaks - Available to all users[/green]")
        self.console.input("Press Enter to continue...")
    
    def handle_network_tweaks(self):
        """Handle network tweaks (root required)"""
        self.console.print("[green]✅ Network Tweaks - Running with root access[/green]")
        self.console.input("Press Enter to continue...")
    
    def handle_performance_tweaks(self):
        """Handle performance tweaks (root required)"""
        self.console.print("[green]✅ Performance Tweaks - Running with root access[/green]")
        self.console.input("Press Enter to continue...")
    
    def handle_security_tweaks(self):
        """Handle security tweaks (root required)"""
        self.console.print("[green]✅ Security Tweaks - Running with root access[/green]")
        self.console.input("Press Enter to continue...")
    
    def handle_backup_restore(self):
        """Handle backup and restore (mixed access)"""
        self.console.print("[green]✅ Backup & Restore - Mixed access level[/green]")
        self.console.input("Press Enter to continue...")
    
    def handle_plugin_system(self):
        """Handle plugin system (user level)"""
        self.console.print("[green]✅ Plugin System - User level access[/green]")
        self.console.input("Press Enter to continue...")
    
    def show_system_info(self):
        """Show system information with real-time monitoring option"""
        self.console.clear()
        self.console.print("[bold cyan]📊 SYSTEM INFORMATION[/bold cyan]\n")
        
        # Show menu for different system info options
        table = Table(show_header=False, box=box.ROUNDED)
        table.add_column("No", style="bold cyan", width=4)
        table.add_column("Option", style="bold white", width=40)
        table.add_column("Description", style="dim white")
        
        options = [
            ("1", "🔴 Real-time Monitor", "Live system monitoring like Task Manager"),
            ("2", "📋 Static System Profile", "Complete system information snapshot"),
            ("3", "💾 Export System Snapshot", "Save current system state to file"),
            ("4", "📈 Performance Benchmark", "Run system performance tests"),
            ("0", "🔙 Back to Main Menu", "Return to main menu")
        ]
        
        for no, option, desc in options:
            table.add_row(no, option, desc)
        
        panel = Panel(
            table,
            title="[bold yellow]📊 SYSTEM INFORMATION OPTIONS[/bold yellow]",
            border_style="bright_yellow",
            padding=(1, 2)
        )
        
        self.console.print(panel)
        
        choice = Prompt.ask("Select an option", default="0")
        
        if choice == "1":
            self.start_realtime_monitor()
        elif choice == "2":
            self.show_static_profile()
        elif choice == "3":
            self.export_system_snapshot()
        elif choice == "4":
            self.run_benchmark()
        elif choice == "0":
            return
        else:
            self.console.print("[red]❌ Invalid choice[/red]")
            self.console.input("Press Enter to continue...")
    
    def start_realtime_monitor(self):
        """Start real-time system monitoring"""
        try:
            from .realtime_monitor import RealtimeMonitor
            
            self.console.clear()
            self.console.print("[bold green]🔴 Starting Real-time Monitor...[/bold green]")
            self.console.print("[dim]Press Ctrl+C to stop monitoring[/dim]\n")
            
            monitor = RealtimeMonitor(self.config, self.logger)
            
            # Ask for monitoring duration
            duration_choice = Prompt.ask(
                "Monitor duration",
                choices=["continuous", "30s", "1m", "5m", "10m"],
                default="continuous"
            )
            
            duration = None
            if duration_choice != "continuous":
                if duration_choice == "30s":
                    duration = 30
                elif duration_choice == "1m":
                    duration = 60
                elif duration_choice == "5m":
                    duration = 300
                elif duration_choice == "10m":
                    duration = 600
            
            # Start monitoring
            monitor.start_monitoring(duration)
            
        except ImportError as e:
            self.console.print(f"[red]❌ Real-time monitor not available: {e}[/red]")
        except Exception as e:
            self.console.print(f"[red]❌ Error starting monitor: {e}[/red]")
        
        self.console.input("\nPress Enter to continue...")
    
    def show_static_profile(self):
        """Show static system profile"""
        if self.profiler:
            self.profiler.show_detailed_profile()
        else:
            self.console.print("[yellow]System profiler not available[/yellow]")
        self.console.input("Press Enter to continue...")
    
    def export_system_snapshot(self):
        """Export system snapshot to file"""
        try:
            from .realtime_monitor import RealtimeMonitor
            
            monitor = RealtimeMonitor(self.config, self.logger)
            filename = monitor.export_snapshot()
            
            if filename:
                self.console.print(f"[green]✅ System snapshot exported successfully![/green]")
            else:
                self.console.print("[red]❌ Failed to export snapshot[/red]")
                
        except Exception as e:
            self.console.print(f"[red]❌ Error exporting snapshot: {e}[/red]")
        
        self.console.input("Press Enter to continue...")
    
    def run_benchmark(self):
        """Run system benchmark"""
        if self.check_and_handle_root_requirement("System Benchmark", "performance_tweaks"):
            try:
                from .benchmark_engine import BenchmarkEngine
                
                self.console.print("[bold yellow]🚀 Starting System Benchmark...[/bold yellow]")
                benchmark = BenchmarkEngine(self.config, self.logger)
                benchmark.run_full_benchmark()
                
            except ImportError:
                self.console.print("[red]❌ Benchmark engine not available[/red]")
            except Exception as e:
                self.console.print(f"[red]❌ Benchmark error: {e}[/red]")
        else:
            self.show_access_denied_message("System Benchmark")
        
        self.console.input("Press Enter to continue...")
    
    def handle_settings(self):
        """Handle settings and configuration"""
        self.console.print("[green]✅ Settings - User level configuration[/green]")
        self.config.display_permission_info()
        self.console.input("Press Enter to continue...")
    
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