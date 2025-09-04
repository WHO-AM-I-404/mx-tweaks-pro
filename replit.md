# MX Tweaks Pro

## Overview
MX Tweaks Pro adalah utility tweaking canggih untuk MX Linux yang dibuat dengan Python 3 dan Rich library. Aplikasi ini membantu pengguna mengoptimasi sistem, membersihkan file tidak perlu, dan mengkustomisasi pengaturan sistem dengan interface yang menarik.

## Features Saat Ini
- **CLI Mode**: Interface command line dengan Rich library yang colorful
- **TUI Mode**: Terminal User Interface dengan dialog boxes
- **GUI Mode**: Graphical User Interface dengan tkinter support
- **System Tweaks**: Optimasi sistem dan pembersihan
- **Appearance Tweaks**: Kustomisasi desktop dan theme management
- **Network Tweaks**: Optimasi koneksi dan TCP stack
- **Performance Tweaks**: Boost performa CPU, memory, dan I/O
- **Security Tweaks**: Hardening sistem dan keamanan
- **Backup System**: Automated backup scheduling dan management
- **Plugin System**: Modular plugin architecture untuk extensibility
- **Root Detection**: Comprehensive root access detection dan management
- **System Info**: Informasi lengkap tentang sistem dengan profiling
- **Benchmark Engine**: Built-in system benchmarking tools

## Project Architecture
```
/
├── main.py                    # Entry point aplikasi
├── src/
│   ├── __init__.py           # Package init
│   ├── cli_interface.py      # Interface CLI dengan Rich
│   ├── tui_interface.py      # Interface TUI dengan dialog
│   ├── tweaks_manager.py     # Manager untuk semua tweaks
│   ├── config_manager.py     # Manajemen konfigurasi
│   ├── backup_manager.py     # Sistem backup/restore
│   └── utils/
│       ├── __init__.py
│       └── logger.py         # Setup logging
└── replit.md                 # Dokumentasi proyek
```

## Tweaks yang Tersedia

### System Tweaks
1. **Nonaktifkan Swap** - Untuk optimasi SSD
2. **Bersihkan Package Cache** - APT cache cleanup
3. **Hapus File Temporary** - Cleanup /tmp dan cache
4. **Optimasi Boot Time** - Disable unnecessary services
5. **Fix Broken Packages** - Repair broken dependencies

### Performance Tweaks
1. **CPU Governor** - Set ke performance mode
2. **Memory Tuning** - Optimasi swappiness dan dirty ratio
3. **Disable Services** - Nonaktifkan service tidak perlu
4. **I/O Scheduler** - Optimasi berdasarkan tipe disk
5. **Preload** - Install dan konfigurasi preload

## Usage
```bash
# Mode CLI (default)
python main.py --cli

# Mode TUI
python main.py --tui

# Mode debug
python main.py --debug
```

## Dependencies
- Python 3.11+
- rich (untuk CLI interface)
- click (untuk argument parsing)
- psutil (untuk system info)
- configparser (untuk konfigurasi)
- dialog (system package untuk TUI)

## Recent Changes
- **2025-09-04**: Initial project setup dengan struktur modular
- **2025-09-04**: Implementasi CLI interface dengan Rich library
- **2025-09-04**: Implementasi TUI interface dengan dialog
- **2025-09-04**: Lengkap system dan performance tweaks
- **2025-09-04**: Setup logging dan configuration management
- **2025-09-04**: Complete advanced features implementation
- **2025-09-04**: Added comprehensive backup scheduler system
- **2025-09-04**: Implemented modular plugin architecture
- **2025-09-04**: Added root access detection and management system
- **2025-09-04**: Enhanced security with proper privilege handling
- **2025-09-04**: Created comprehensive documentation (README.md)
- **2025-09-04**: Added setup.sh with root detection for installation
- **2025-09-04**: **FINAL DEBUGGING SESSION COMPLETED**:
  - ✅ Fixed all syntax errors in realtime monitor module
  - ✅ Resolved CLI interface diagnostic errors and duplicate methods
  - ✅ Successfully tested all system modules with comprehensive functionality
  - ✅ Cleaned project structure, removed unused files
  - ✅ Verified executable `mx-tweaks-pro` command functionality
  - ✅ Validated comprehensive system profiling and monitoring
  - ✅ Confirmed root access detection working with clear messaging
  - ✅ All LSP diagnostics resolved - production ready code

## User Preferences
- Interface: CLI, TUI, dan GUI tersedia dengan user preference
- Bahasa: English untuk version 2.1 (user request)
- Style: Modern, colorful, user-friendly dengan Rich library
- Safety: Konfirmasi untuk operasi berisiko dan automatic backup
- Root Access: Clear messaging dan flexible permission handling
- Security: Proper privilege detection dan escalation support

## Development Notes
- Root access detection dengan os.geteuid() dan clear error messaging
- Flexible permissions: non-root features tetap accessible
- Backup otomatis sebelum melakukan perubahan kritis
- Logging lengkap untuk debugging dan audit
- Modular design untuk easy maintenance
- Plugin system untuk extensibility
- Support untuk sudo dan pkexec execution
- Comprehensive error handling dan user guidance
- Security-first approach dengan proper privilege management

## Completed Features
- ✅ Appearance Tweaks untuk desktop customization
- ✅ Network Tweaks untuk optimasi koneksi
- ✅ Security Tweaks untuk hardening sistem
- ✅ GUI mode dengan tkinter support
- ✅ Automated backup scheduling dengan BackupScheduler
- ✅ Plugin system untuk custom tweaks dan extensibility
- ✅ Root access detection dan management
- ✅ Comprehensive documentation

## Future Enhancements
- Advanced GUI dengan PyQt/GTK
- Cloud backup integration
- Real-time system monitoring
- Advanced plugin marketplace
- Multi-distribution support beyond MX Linux
- Web-based management interface