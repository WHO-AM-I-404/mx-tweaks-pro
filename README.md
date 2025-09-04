# MX Tweaks Pro

## Overview
MX Tweaks Pro adalah utility tweaking canggih untuk MX Linux yang dibuat dengan Python 3 dan Rich library. Aplikasi ini membantu pengguna mengoptimasi sistem, membersihkan file tidak perlu, dan mengkustomisasi pengaturan sistem dengan interface yang menarik.

## Features Saat Ini
- **CLI Mode**: Interface command line dengan Rich library yang colorful
- **TUI Mode**: Terminal User Interface dengan dialog boxes
- **System Tweaks**: Optimasi sistem dan pembersihan
- **Performance Tweaks**: Boost performa CPU, memory, dan I/O
- **System Info**: Informasi lengkap tentang sistem
- **Backup System**: Backup dan restore konfigurasi (struktur sudah siap)

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
└── README.md                 # Dokumentasi proyek
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

## User Preferences
- Interface: CLI dan TUI keduanya tersedia
- Bahasa: Indonesia untuk user-facing text
- Style: Modern, colorful, user-friendly
- Safety: Konfirmasi untuk operasi berisiko

## Development Notes
- Semua tweaks system memerlukan sudo access
- Backup otomatis sebelum melakukan perubahan kritis
- Logging lengkap untuk debugging dan audit
- Modular design untuk easy maintenance

## Future Features (Coming Soon)
- Appearance Tweaks untuk desktop customization
- Network Tweaks untuk optimasi koneksi
- Security Tweaks untuk hardening sistem
- GUI mode dengan tkinter atau PyQt
- Automated backup scheduling
- Plugin system untuk custom tweaks
