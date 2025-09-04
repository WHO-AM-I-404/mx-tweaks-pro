#!/usr/bin/env python3
"""
MX Tweaks Pro - Utility Tweaking Canggih untuk MX Linux
Dibuat dengan Python 3 dan Rich library untuk tampilan yang keren
"""

import sys
import os
import argparse
from pathlib import Path

# Import modul-modul utama
from src.cli_interface import CLIInterface
from src.config_manager import ConfigManager
from src.utils.logger import setup_logger

def main():
    """Fungsi utama aplikasi MX Tweaks Pro"""
    parser = argparse.ArgumentParser(
        description="MX Tweaks Pro - Utility Tweaking Canggih untuk MX Linux",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Mode yang tersedia:
  --cli     Mode Command Line Interface (default)
  --tui     Mode Terminal User Interface
  --gui     Mode Graphical User Interface (coming soon)

Contoh penggunaan:
  python main.py --cli
  python main.py --tui
        """
    )
    
    parser.add_argument('--cli', action='store_true', help='Jalankan dalam mode CLI')
    parser.add_argument('--tui', action='store_true', help='Jalankan dalam mode TUI')
    parser.add_argument('--gui', action='store_true', help='Jalankan dalam mode GUI (segera hadir)')
    parser.add_argument('--debug', action='store_true', help='Aktifkan mode debug')
    
    args = parser.parse_args()
    
    # Setup logger
    logger = setup_logger(debug=args.debug)
    
    # Inisialisasi config manager
    config = ConfigManager()
    
    # Cek apakah berjalan sebagai root (diperlukan untuk beberapa tweaks)
    if os.geteuid() != 0:
        print("⚠️  Peringatan: Beberapa tweaks memerlukan akses root.")
        print("💡 Jalankan dengan: sudo python main.py")
        print()
    
    # Tentukan mode interface
    if args.tui:
        from src.tui_interface import TUIInterface
        interface = TUIInterface(config, logger)
    elif args.gui:
        print("🚧 Mode GUI sedang dalam pengembangan...")
        sys.exit(1)
    else:
        # Default ke CLI
        interface = CLIInterface(config, logger)
    
    try:
        # Jalankan interface yang dipilih
        interface.run()
    except KeyboardInterrupt:
        print("\n\n👋 Terima kasih telah menggunakan MX Tweaks Pro!")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error tidak terduga: {e}")
        print(f"❌ Terjadi error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()