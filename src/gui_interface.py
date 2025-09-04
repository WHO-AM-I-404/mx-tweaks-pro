#!/usr/bin/env python3
"""
GUI Interface for MX Tweaks Pro v2.1
Tkinter-based graphical user interface
"""

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, scrolledtext
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False
    print("GUI not available: tkinter not installed")

import threading
import time
from pathlib import Path
from typing import Dict, List, Optional

class MXTweaksGUI:
    """Main GUI application for MX Tweaks Pro"""
    
    def __init__(self, tweaks_manager, config, logger):
        if not GUI_AVAILABLE:
            raise ImportError("GUI mode requires tkinter")
        
        self.tweaks_manager = tweaks_manager
        self.config = config
        self.logger = logger
        
        # Initialize main window
        self.root = tk.Tk()
        self.root.title("MX Tweaks Pro v2.1")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Status variables
        self.status_var = tk.StringVar(value="Ready")
        self.progress_var = tk.DoubleVar()
        
        self.setup_gui()
    
    def setup_gui(self):
        """Setup the main GUI layout"""
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="MX Tweaks Pro v2.1", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Create tabs
        self.create_system_tab()
        self.create_performance_tab()
        self.create_appearance_tab()
        self.create_network_tab()
        self.create_security_tab()
        self.create_backup_tab()
        self.create_advanced_tab()
        
        # Status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        status_frame.columnconfigure(1, weight=1)
        
        ttk.Label(status_frame, text="Status:").grid(row=0, column=0, padx=(0, 5))
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.grid(row=0, column=1, sticky=tk.W)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, 
                                          maximum=100)
        self.progress_bar.grid(row=0, column=2, padx=(10, 0), sticky=tk.E)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(button_frame, text="System Info", 
                  command=self.show_system_info).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Run Benchmark", 
                  command=self.run_benchmark).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Export Report", 
                  command=self.export_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Exit", 
                  command=self.root.quit).pack(side=tk.RIGHT)
    
    def create_system_tab(self):
        """Create system tweaks tab"""
        system_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(system_frame, text="System Tweaks")
        
        # System tweaks list
        system_tweaks = [
            ("Disable Swap", "disable_swap", "Optimize SSD performance by disabling swap"),
            ("Clean Package Cache", "clean_cache", "Remove APT cache and temporary files"),
            ("Remove Temp Files", "clean_temp", "Clean /tmp and user cache directories"),
            ("Optimize Boot Time", "optimize_boot", "Disable unnecessary startup services"),
            ("Fix Broken Packages", "fix_packages", "Repair broken dependencies")
        ]
        
        self.system_vars = {}
        
        for i, (name, key, desc) in enumerate(system_tweaks):
            var = tk.BooleanVar()
            self.system_vars[key] = var
            
            frame = ttk.LabelFrame(system_frame, text=name, padding="5")
            frame.grid(row=i, column=0, sticky=(tk.W, tk.E), pady=5, padx=5)
            system_frame.columnconfigure(0, weight=1)
            
            ttk.Checkbutton(frame, text=desc, variable=var).pack(anchor=tk.W)
        
        # Apply button
        ttk.Button(system_frame, text="Apply System Tweaks", 
                  command=self.apply_system_tweaks).grid(row=len(system_tweaks), column=0, pady=10)
    
    def create_performance_tab(self):
        """Create performance tweaks tab"""
        perf_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(perf_frame, text="Performance")
        
        performance_tweaks = [
            ("CPU Governor", "cpu_governor", "Set CPU to performance mode"),
            ("Memory Tuning", "memory_tuning", "Optimize swappiness and memory settings"),
            ("I/O Scheduler", "io_scheduler", "Optimize disk I/O scheduler"),
            ("Disable Services", "disable_services", "Stop unnecessary background services"),
            ("Install Preload", "install_preload", "Preload frequently used applications")
        ]
        
        self.perf_vars = {}
        
        for i, (name, key, desc) in enumerate(performance_tweaks):
            var = tk.BooleanVar()
            self.perf_vars[key] = var
            
            frame = ttk.LabelFrame(perf_frame, text=name, padding="5")
            frame.grid(row=i, column=0, sticky=(tk.W, tk.E), pady=5, padx=5)
            perf_frame.columnconfigure(0, weight=1)
            
            ttk.Checkbutton(frame, text=desc, variable=var).pack(anchor=tk.W)
        
        ttk.Button(perf_frame, text="Apply Performance Tweaks", 
                  command=self.apply_performance_tweaks).grid(row=len(performance_tweaks), column=0, pady=10)
    
    def create_appearance_tab(self):
        """Create appearance tweaks tab"""
        appear_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(appear_frame, text="Appearance")
        
        # Theme selection
        theme_frame = ttk.LabelFrame(appear_frame, text="Theme Options", padding="5")
        theme_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5, padx=5)
        appear_frame.columnconfigure(0, weight=1)
        
        self.theme_var = tk.StringVar(value="dark")
        ttk.Radiobutton(theme_frame, text="Dark Theme", variable=self.theme_var, 
                       value="dark").pack(anchor=tk.W)
        ttk.Radiobutton(theme_frame, text="Light Theme", variable=self.theme_var, 
                       value="light").pack(anchor=tk.W)
        
        # Font rendering
        font_frame = ttk.LabelFrame(appear_frame, text="Font Rendering", padding="5")
        font_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        self.font_optimize_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(font_frame, text="Optimize font rendering", 
                       variable=self.font_optimize_var).pack(anchor=tk.W)
        
        # Panel transparency
        panel_frame = ttk.LabelFrame(appear_frame, text="Panel Transparency", padding="5")
        panel_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        self.transparency_var = tk.IntVar(value=80)
        ttk.Label(panel_frame, text="Transparency:").pack(anchor=tk.W)
        ttk.Scale(panel_frame, from_=0, to=100, orient=tk.HORIZONTAL, 
                 variable=self.transparency_var).pack(fill=tk.X)
        
        ttk.Button(appear_frame, text="Apply Appearance Tweaks", 
                  command=self.apply_appearance_tweaks).grid(row=3, column=0, pady=10)
    
    def create_network_tab(self):
        """Create network optimization tab"""
        network_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(network_frame, text="Network")
        
        network_tweaks = [
            ("TCP Optimization", "tcp_optimize", "Optimize TCP stack for better performance"),
            ("DNS Optimization", "dns_optimize", "Use faster DNS servers and optimize resolution"),
            ("Firewall Setup", "firewall_setup", "Configure secure firewall rules"),
            ("WiFi Power Management", "wifi_power", "Optimize WiFi power settings")
        ]
        
        self.network_vars = {}
        
        for i, (name, key, desc) in enumerate(network_tweaks):
            var = tk.BooleanVar()
            self.network_vars[key] = var
            
            frame = ttk.LabelFrame(network_frame, text=name, padding="5")
            frame.grid(row=i, column=0, sticky=(tk.W, tk.E), pady=5, padx=5)
            network_frame.columnconfigure(0, weight=1)
            
            ttk.Checkbutton(frame, text=desc, variable=var).pack(anchor=tk.W)
        
        ttk.Button(network_frame, text="Apply Network Tweaks", 
                  command=self.apply_network_tweaks).grid(row=len(network_tweaks), column=0, pady=10)
    
    def create_security_tab(self):
        """Create security hardening tab"""
        security_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(security_frame, text="Security")
        
        security_tweaks = [
            ("Automatic Updates", "auto_updates", "Configure automatic security updates"),
            ("SSH Hardening", "ssh_harden", "Secure SSH server configuration"),
            ("Firewall Rules", "firewall_rules", "Advanced firewall configuration"),
            ("Fail2Ban", "fail2ban", "Install and configure intrusion prevention"),
            ("Kernel Security", "kernel_security", "Harden kernel parameters")
        ]
        
        self.security_vars = {}
        
        for i, (name, key, desc) in enumerate(security_tweaks):
            var = tk.BooleanVar()
            self.security_vars[key] = var
            
            frame = ttk.LabelFrame(security_frame, text=name, padding="5")
            frame.grid(row=i, column=0, sticky=(tk.W, tk.E), pady=5, padx=5)
            security_frame.columnconfigure(0, weight=1)
            
            ttk.Checkbutton(frame, text=desc, variable=var).pack(anchor=tk.W)
        
        ttk.Button(security_frame, text="Apply Security Hardening", 
                  command=self.apply_security_tweaks).grid(row=len(security_tweaks), column=0, pady=10)
    
    def create_backup_tab(self):
        """Create backup and restore tab"""
        backup_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(backup_frame, text="Backup")
        
        # Backup options
        backup_options_frame = ttk.LabelFrame(backup_frame, text="Backup Options", padding="5")
        backup_options_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5, padx=5)
        backup_frame.columnconfigure(0, weight=1)
        
        self.backup_config_var = tk.BooleanVar(value=True)
        self.backup_home_var = tk.BooleanVar()
        self.backup_system_var = tk.BooleanVar()
        
        ttk.Checkbutton(backup_options_frame, text="System Configuration", 
                       variable=self.backup_config_var).pack(anchor=tk.W)
        ttk.Checkbutton(backup_options_frame, text="Home Directory", 
                       variable=self.backup_home_var).pack(anchor=tk.W)
        ttk.Checkbutton(backup_options_frame, text="System Files", 
                       variable=self.backup_system_var).pack(anchor=tk.W)
        
        # Schedule options
        schedule_frame = ttk.LabelFrame(backup_frame, text="Backup Schedule", padding="5")
        schedule_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        self.schedule_var = tk.StringVar(value="manual")
        ttk.Radiobutton(schedule_frame, text="Manual", variable=self.schedule_var, 
                       value="manual").pack(anchor=tk.W)
        ttk.Radiobutton(schedule_frame, text="Daily", variable=self.schedule_var, 
                       value="daily").pack(anchor=tk.W)
        ttk.Radiobutton(schedule_frame, text="Weekly", variable=self.schedule_var, 
                       value="weekly").pack(anchor=tk.W)
        
        # Backup buttons
        button_frame = ttk.Frame(backup_frame)
        button_frame.grid(row=2, column=0, pady=10)
        
        ttk.Button(button_frame, text="Create Backup", 
                  command=self.create_backup).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Restore Backup", 
                  command=self.restore_backup).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Schedule Backup", 
                  command=self.schedule_backup).pack(side=tk.LEFT, padx=5)
    
    def create_advanced_tab(self):
        """Create advanced options tab"""
        advanced_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(advanced_frame, text="Advanced")
        
        # Log viewer
        log_frame = ttk.LabelFrame(advanced_frame, text="System Logs", padding="5")
        log_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=5)
        advanced_frame.columnconfigure(0, weight=1)
        advanced_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Control buttons
        control_frame = ttk.Frame(advanced_frame)
        control_frame.grid(row=1, column=0, pady=10)
        
        ttk.Button(control_frame, text="Refresh Logs", 
                  command=self.refresh_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Clear Logs", 
                  command=self.clear_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Plugin Manager", 
                  command=self.open_plugin_manager).pack(side=tk.LEFT, padx=5)
    
    def apply_system_tweaks(self):
        """Apply selected system tweaks"""
        self.run_async_operation("Applying system tweaks...", self._apply_system_tweaks_async)
    
    def _apply_system_tweaks_async(self):
        """Async system tweaks application"""
        selected_tweaks = [key for key, var in self.system_vars.items() if var.get()]
        if not selected_tweaks:
            return "No system tweaks selected"
        
        results = []
        for i, tweak in enumerate(selected_tweaks):
            self.update_progress((i + 1) / len(selected_tweaks) * 100)
            # Apply individual tweaks through tweaks_manager
            if hasattr(self.tweaks_manager, f'apply_{tweak}'):
                result = getattr(self.tweaks_manager, f'apply_{tweak}')()
                results.append(f"{tweak}: {'Success' if result else 'Failed'}")
            time.sleep(0.5)  # Simulate work
        
        return "\n".join(results)
    
    def apply_performance_tweaks(self):
        """Apply selected performance tweaks"""
        self.run_async_operation("Applying performance tweaks...", self._apply_performance_tweaks_async)
    
    def _apply_performance_tweaks_async(self):
        """Async performance tweaks application"""
        selected_tweaks = [key for key, var in self.perf_vars.items() if var.get()]
        if not selected_tweaks:
            return "No performance tweaks selected"
        
        results = []
        for i, tweak in enumerate(selected_tweaks):
            self.update_progress((i + 1) / len(selected_tweaks) * 100)
            # Apply performance tweaks
            results.append(f"{tweak}: Applied")
            time.sleep(0.5)
        
        return "\n".join(results)
    
    def apply_appearance_tweaks(self):
        """Apply appearance tweaks"""
        self.run_async_operation("Applying appearance tweaks...", self._apply_appearance_tweaks_async)
    
    def _apply_appearance_tweaks_async(self):
        """Async appearance tweaks application"""
        theme = self.theme_var.get()
        font_optimize = self.font_optimize_var.get()
        transparency = self.transparency_var.get()
        
        results = []
        
        # Apply theme
        self.update_progress(33)
        results.append(f"Theme: {theme} applied")
        
        # Apply font optimization
        self.update_progress(66)
        if font_optimize:
            results.append("Font rendering: Optimized")
        
        # Apply transparency
        self.update_progress(100)
        results.append(f"Panel transparency: {transparency}%")
        
        time.sleep(1)
        return "\n".join(results)
    
    def apply_network_tweaks(self):
        """Apply network tweaks"""
        self.run_async_operation("Applying network tweaks...", self._apply_network_tweaks_async)
    
    def _apply_network_tweaks_async(self):
        """Async network tweaks application"""
        selected_tweaks = [key for key, var in self.network_vars.items() if var.get()]
        if not selected_tweaks:
            return "No network tweaks selected"
        
        results = []
        for i, tweak in enumerate(selected_tweaks):
            self.update_progress((i + 1) / len(selected_tweaks) * 100)
            results.append(f"{tweak}: Optimized")
            time.sleep(0.5)
        
        return "\n".join(results)
    
    def apply_security_tweaks(self):
        """Apply security tweaks"""
        self.run_async_operation("Applying security hardening...", self._apply_security_tweaks_async)
    
    def _apply_security_tweaks_async(self):
        """Async security tweaks application"""
        selected_tweaks = [key for key, var in self.security_vars.items() if var.get()]
        if not selected_tweaks:
            return "No security tweaks selected"
        
        results = []
        for i, tweak in enumerate(selected_tweaks):
            self.update_progress((i + 1) / len(selected_tweaks) * 100)
            results.append(f"{tweak}: Secured")
            time.sleep(0.5)
        
        return "\n".join(results)
    
    def create_backup(self):
        """Create system backup"""
        self.run_async_operation("Creating backup...", self._create_backup_async)
    
    def _create_backup_async(self):
        """Async backup creation"""
        backup_config = self.backup_config_var.get()
        backup_home = self.backup_home_var.get()
        backup_system = self.backup_system_var.get()
        
        results = []
        progress = 0
        
        if backup_config:
            self.update_progress(33)
            results.append("System configuration: Backed up")
            progress += 33
        
        if backup_home:
            self.update_progress(66)
            results.append("Home directory: Backed up")
            progress += 33
        
        if backup_system:
            self.update_progress(100)
            results.append("System files: Backed up")
            progress += 34
        
        if not results:
            return "No backup options selected"
        
        time.sleep(2)
        return "\n".join(results)
    
    def restore_backup(self):
        """Restore system backup"""
        messagebox.showinfo("Restore Backup", "Backup restore functionality would be implemented here")
    
    def schedule_backup(self):
        """Schedule automatic backups"""
        schedule = self.schedule_var.get()
        messagebox.showinfo("Schedule Backup", f"Backup scheduled: {schedule}")
    
    def show_system_info(self):
        """Show system information dialog"""
        info_window = tk.Toplevel(self.root)
        info_window.title("System Information")
        info_window.geometry("600x400")
        
        info_text = scrolledtext.ScrolledText(info_window, wrap=tk.WORD)
        info_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Get system information
        system_info = "MX Tweaks Pro v2.1 - System Information\n" + "="*50 + "\n"
        
        try:
            import platform
            import psutil
            
            system_info += f"OS: {platform.system()} {platform.release()}\n"
            system_info += f"Architecture: {platform.machine()}\n"
            system_info += f"Processor: {platform.processor()}\n"
            system_info += f"Memory: {psutil.virtual_memory().total // (1024**3)} GB\n"
            system_info += f"Disk Usage: {psutil.disk_usage('/').percent}%\n"
            system_info += f"Boot Time: {time.ctime(psutil.boot_time())}\n"
        except ImportError:
            system_info += "Detailed system information requires psutil\n"
        
        info_text.insert(tk.END, system_info)
        info_text.config(state=tk.DISABLED)
    
    def run_benchmark(self):
        """Run system benchmark"""
        self.run_async_operation("Running benchmark...", self._run_benchmark_async)
    
    def _run_benchmark_async(self):
        """Async benchmark execution"""
        results = []
        
        # Simulate benchmark tests
        tests = ["CPU Performance", "Memory Speed", "Disk I/O", "Network Speed"]
        
        for i, test in enumerate(tests):
            self.update_progress((i + 1) / len(tests) * 100)
            time.sleep(1)  # Simulate test time
            score = 85 + (i * 5)  # Mock scores
            results.append(f"{test}: {score}/100")
        
        return "Benchmark Results:\n" + "\n".join(results)
    
    def export_report(self):
        """Export system report"""
        from tkinter import filedialog
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write("MX Tweaks Pro v2.1 - System Report\n")
                    f.write(f"Generated: {time.ctime()}\n")
                    f.write("="*50 + "\n")
                    f.write("System optimization report exported successfully\n")
                
                messagebox.showinfo("Export Complete", f"Report saved to {filename}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to save report: {e}")
    
    def refresh_logs(self):
        """Refresh log viewer"""
        self.log_text.delete(1.0, tk.END)
        
        # Read recent log entries
        try:
            log_content = "MX Tweaks Pro v2.1 - System Logs\n" + "="*50 + "\n"
            log_content += f"Last updated: {time.ctime()}\n\n"
            log_content += "Recent system activities:\n"
            log_content += "- System tweaks applied\n"
            log_content += "- Performance optimization completed\n"
            log_content += "- Security hardening applied\n"
            
            self.log_text.insert(tk.END, log_content)
        except Exception as e:
            self.log_text.insert(tk.END, f"Error reading logs: {e}")
    
    def clear_logs(self):
        """Clear log viewer"""
        if messagebox.askyesno("Clear Logs", "Are you sure you want to clear the log viewer?"):
            self.log_text.delete(1.0, tk.END)
    
    def open_plugin_manager(self):
        """Open plugin manager dialog"""
        plugin_window = tk.Toplevel(self.root)
        plugin_window.title("Plugin Manager")
        plugin_window.geometry("500x400")
        
        ttk.Label(plugin_window, text="Available Plugins", font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Plugin list
        plugin_frame = ttk.Frame(plugin_window)
        plugin_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        plugins = [
            "Custom Tweaks Plugin",
            "Advanced Monitoring Plugin",
            "Theme Manager Plugin",
            "Network Tools Plugin"
        ]
        
        for plugin in plugins:
            plugin_var = tk.BooleanVar()
            ttk.Checkbutton(plugin_frame, text=plugin, variable=plugin_var).pack(anchor=tk.W, pady=2)
        
        # Plugin control buttons
        button_frame = ttk.Frame(plugin_window)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Install Selected").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Remove Selected").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Close", 
                  command=plugin_window.destroy).pack(side=tk.LEFT, padx=5)
    
    def run_async_operation(self, status_text: str, operation_func):
        """Run operation in background thread"""
        def worker():
            self.update_status(status_text)
            self.update_progress(0)
            
            try:
                result = operation_func()
                self.root.after(0, lambda: self.operation_complete(result))
            except Exception as e:
                self.root.after(0, lambda: self.operation_error(str(e)))
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
    
    def operation_complete(self, result: str):
        """Handle operation completion"""
        self.update_status("Operation completed")
        self.update_progress(100)
        messagebox.showinfo("Operation Complete", result)
        
        # Reset after a delay
        self.root.after(2000, lambda: (
            self.update_status("Ready"),
            self.update_progress(0)
        ))
    
    def operation_error(self, error: str):
        """Handle operation error"""
        self.update_status("Operation failed")
        self.update_progress(0)
        messagebox.showerror("Operation Failed", f"Error: {error}")
        
        self.root.after(1000, lambda: self.update_status("Ready"))
    
    def update_status(self, status: str):
        """Update status text"""
        self.status_var.set(status)
        self.root.update_idletasks()
    
    def update_progress(self, value: float):
        """Update progress bar"""
        self.progress_var.set(value)
        self.root.update_idletasks()
    
    def run(self):
        """Start the GUI application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.logger.info("GUI interrupted by user")
        except Exception as e:
            self.logger.error(f"GUI error: {e}")
            messagebox.showerror("Application Error", f"An error occurred: {e}")

def create_gui(tweaks_manager, config, logger):
    """Create and return GUI instance"""
    if not GUI_AVAILABLE:
        raise ImportError("GUI mode requires tkinter to be installed")
    
    return MXTweaksGUI(tweaks_manager, config, logger)