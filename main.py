#!/usr/bin/env python3
"""
MX Tweaks Pro v2.1 - Advanced Linux System Optimization Utility
Built with Python 3 and Rich library for superior user experience
With comprehensive root access detection and management
"""

import sys
import os
import argparse
from pathlib import Path

# Import core modules
from src.cli_interface import CLIInterface
from src.config_manager import ConfigManager
from src.utils.logger import setup_logger
from src.system_profiler import SystemProfiler

def check_system_requirements():
    """Check basic system requirements"""
    from rich.console import Console
    console = Console()
    
    # Check Python version
    if sys.version_info < (3, 8):
        console.print("[bold red]❌ Python 3.8 or higher is required[/bold red]")
        console.print(f"[red]Current version: {sys.version}[/red]")
        sys.exit(1)
    
    # Check if running on supported system
    try:
        import platform
        if platform.system() != 'Linux':
            console.print("[bold yellow]⚠️ MX Tweaks Pro is designed for Linux systems[/bold yellow]")
            console.print("[yellow]Some features may not work properly on other systems[/yellow]")
    except Exception:
        pass

def handle_root_requirements(args, config):
    """Handle root requirements based on the selected mode and operations"""
    from rich.console import Console
    console = Console()
    
    # Operations that absolutely require root
    root_required_modes = ['bench']
    
    # Check if this mode requires root
    if any(getattr(args, mode, False) for mode in root_required_modes):
        if not config.require_root_access(f"{', '.join(root_required_modes)} operations"):
            console.print("[red]Exiting due to insufficient privileges.[/red]")
            sys.exit(1)
    
    return True

def main():
    """Main entry point for MX Tweaks Pro v2.1"""
    # Check system requirements first
    check_system_requirements()
    
    parser = argparse.ArgumentParser(
        description="MX Tweaks Pro v2.1 - Advanced Linux System Optimization Utility with Root Access Management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available modes:
  --cli     Command Line Interface (default)
  --tui     Terminal User Interface
  --gui     Graphical User Interface
  --bench   Run system benchmarks (requires root)
  --safe    Safe mode (backup before every change)
  --debug   Enable debug logging
  --profile Show detailed system profile

Root Access:
  Some operations require root privileges. The program will:
  • Show clear messages when root is required
  • Offer to restart with pkexec for GUI access
  • Allow user operations to continue without root

Usage examples:
  mx-tweaks-pro --cli              # CLI mode (user level)
  sudo mx-tweaks-pro --cli         # CLI mode (full access)
  pkexec mx-tweaks-pro --gui       # GUI mode with root
  mx-tweaks-pro --bench            # Benchmarks (will prompt for root)
        """
    )
    
    parser.add_argument('--cli', action='store_true', help='Run in CLI mode')
    parser.add_argument('--tui', action='store_true', help='Run in TUI mode')
    parser.add_argument('--gui', action='store_true', help='Run in GUI mode (coming soon)')
    parser.add_argument('--bench', action='store_true', help='Run system benchmarks')
    parser.add_argument('--safe', action='store_true', help='Enable safe mode with auto-backup')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--profile', action='store_true', help='Show detailed system profile')
    
    args = parser.parse_args()
    
    # Setup logger
    logger = setup_logger(debug=args.debug)
    
    # Initialize config manager
    config = ConfigManager()
    
    # Initialize system profiler
    profiler = SystemProfiler(logger)
    
    # Initialize early for root check
    from rich.console import Console
    console = Console()
    
    # Check and handle root access
    if not config.check_root_access():
        # Display permission information
        config.display_permission_info()
        
        # For GUI mode, we can continue without root (will prompt when needed)
        if not args.gui:
            console.print("\n[yellow]Starting in user mode with limited functionality...[/yellow]")
            console.print("[dim]Use 'sudo mx-tweaks-pro' for full system optimization features.[/dim]\n")
    else:
        console.print("[bold green]✅ Running with root privileges - All features available[/bold green]\n")
    
    # Handle special modes
    if args.profile:
        profiler.show_detailed_profile()
        sys.exit(0)
    
    if args.bench:
        # Check root access for benchmarks
        if not config.check_operation_permissions('performance_tweaks'):
            sys.exit(1)
        
        from src.benchmark_engine import BenchmarkEngine
        benchmark = BenchmarkEngine(config, logger)
        benchmark.run_full_benchmark()
        sys.exit(0)
    
    # Handle root requirements for specific operations
    handle_root_requirements(args, config)
    
    # Set safe mode
    if args.safe:
        config.set('general', 'safe_mode', 'true')
        console.print("🛡️  [green]Safe mode enabled - all changes will be backed up[/green]")
    
    # Determine interface mode
    if args.tui:
        from src.tui_interface import TUIInterface
        interface = TUIInterface(config, logger, profiler)
    elif args.gui:
        try:
            from src.gui_interface import GUIInterface
            interface = GUIInterface(config, logger)
        except ImportError as e:
            console.print("[red]❌ GUI dependencies not available[/red]")
            console.print(f"[red]Error: {e}[/red]")
            console.print("[yellow]Please install tkinter: sudo apt install python3-tk[/yellow]")
            sys.exit(1)
    else:
        # Default to CLI
        interface = CLIInterface(config, logger, profiler)
    
    # Start the interface
    try:
        interface.run()
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Thank you for using MX Tweaks Pro v2.1![/yellow]")
        sys.exit(0)
    except PermissionError as e:
        console.print(f"[red]❌ Permission denied: {e}[/red]")
        console.print("[yellow]Try running with sudo for system-level operations.[/yellow]")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        console.print(f"[red]❌ An error occurred: {e}[/red]")
        if args.debug:
            import traceback
            console.print("[dim]Full traceback:[/dim]")
            console.print(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()