#!/usr/bin/env python3
"""
TUI Interface untuk MX Tweaks Pro
Menggunakan dialog untuk tampilan terminal user interface yang interaktif
"""

import os
import sys
import subprocess
from .tweaks_manager import TweaksManager
from .backup_manager import BackupManager

class TUIInterface:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.tweaks = TweaksManager(config, logger)
        self.backup = BackupManager(config, logger)
        
        # Cek apakah dialog tersedia
        if not self.check_dialog_available():
            print("❌ Dialog tidak tersedia. Install dengan: sudo apt-get install dialog")
            sys.exit(1)
    
    def check_dialog_available(self):
        """Cek apakah dialog command tersedia"""
        try:
            subprocess.run(['which', 'dialog'], capture_output=True, check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def dialog_cmd(self, *args):
        """Jalankan dialog command"""
        try:
            result = subprocess.run(
                ['dialog'] + list(args),
                capture_output=True,
                text=True,
                stderr=subprocess.PIPE
            )
            return result.returncode == 0, result.stderr.strip()
        except Exception as e:
            self.logger.error(f"Dialog error: {e}")
            return False, str(e)
    
    def show_welcome(self):
        """Tampilkan welcome screen"""
        welcome_text = """Selamat datang di MX Tweaks Pro!

Utility tweaking canggih untuk MX Linux yang membantu Anda:

• Mengoptimasi performa sistem
• Membersihkan file tidak perlu
• Mengkustomisasi pengaturan
• Backup & restore konfigurasi
• Dan masih banyak lagi!

Dibuat dengan ❤️ untuk komunitas MX Linux
Versi: 1.0.0"""
        
        self.dialog_cmd(
            '--title', 'MX Tweaks Pro v1.0.0',
            '--msgbox', welcome_text,
            '18', '60'
        )
    
    def show_main_menu(self):
        """Tampilkan menu utama TUI"""
        menu_items = [
            ('1', '🔧 System Tweaks - Optimasi sistem dan performa'),
            ('2', '🎨 Appearance Tweaks - Kustomisasi tampilan (Coming Soon)'),
            ('3', '🌐 Network Tweaks - Optimasi koneksi (Coming Soon)'),
            ('4', '⚡ Performance Tweaks - Boost performa sistem'),
            ('5', '🛡️ Security Tweaks - Pengaturan keamanan (Coming Soon)'),
            ('6', '💾 Backup & Restore - Kelola backup (Coming Soon)'),
            ('7', '⚙️ Advanced Settings - Pengaturan lanjutan (Coming Soon)'),
            ('8', '📊 System Info - Informasi sistem lengkap'),
            ('0', '🚪 Keluar - Keluar dari aplikasi')
        ]
        
        # Format menu untuk dialog
        menu_args = ['--title', 'MX Tweaks Pro - Menu Utama',
                    '--menu', 'Pilih menu yang ingin Anda akses:',
                    '20', '80', '9']
        
        for item, desc in menu_items:
            menu_args.extend([item, desc])
        
        success, choice = self.dialog_cmd(*menu_args)
        
        if success and choice:
            return choice.strip()
        return None
    
    def show_system_tweaks_menu(self):
        """Menu untuk system tweaks"""
        menu_items = [
            ('1', '🚀 Nonaktifkan Swap - Untuk optimasi SSD'),
            ('2', '📦 Bersihkan Package Cache - Hemat storage'),
            ('3', '🗑️ Hapus File Temporary - Bersihkan file sementara'),
            ('4', '⚡ Optimasi Boot Time - Percepat booting'),
            ('5', '🔧 Fix Broken Packages - Perbaiki package rusak'),
            ('0', '🔙 Kembali ke Menu Utama')
        ]
        
        menu_args = ['--title', 'System Tweaks',
                    '--menu', 'Pilih tweak sistem yang ingin diterapkan:',
                    '15', '70', '6']
        
        for item, desc in menu_items:
            menu_args.extend([item, desc])
        
        success, choice = self.dialog_cmd(*menu_args)
        
        if success and choice:
            choice = choice.strip()
            if choice == '1':
                self.confirm_and_run_tweak(
                    "Nonaktifkan Swap",
                    "Apakah Anda yakin ingin menonaktifkan swap? Ini dapat mempengaruhi performa jika RAM penuh.",
                    self.tweaks.disable_swap
                )
            elif choice == '2':
                self.confirm_and_run_tweak(
                    "Bersihkan Package Cache",
                    "Membersihkan cache package manager untuk menghemat storage.",
                    self.tweaks.clean_package_cache
                )
            elif choice == '3':
                self.confirm_and_run_tweak(
                    "Hapus File Temporary",
                    "Menghapus file temporary yang sudah tidak terpakai.",
                    self.tweaks.clean_temp_files
                )
            elif choice == '4':
                self.confirm_and_run_tweak(
                    "Optimasi Boot Time",
                    "Menganalisa dan mengoptimasi waktu boot sistem.",
                    self.tweaks.optimize_boot_time
                )
            elif choice == '5':
                self.confirm_and_run_tweak(
                    "Fix Broken Packages",
                    "Memperbaiki dependency package yang rusak.",
                    self.tweaks.fix_broken_packages
                )
            elif choice == '0':
                return
            
            # Kembali ke menu system tweaks setelah menjalankan tweak
            if choice != '0':
                self.show_system_tweaks_menu()
    
    def show_performance_tweaks_menu(self):
        """Menu untuk performance tweaks"""
        menu_items = [
            ('1', '🎯 Optimasi CPU Governor - Set ke mode performance'),
            ('2', '💾 Tuning Memory - Optimasi parameter memory'),
            ('3', '🔥 Disable Services - Nonaktifkan service tidak perlu'),
            ('4', '⚡ I/O Scheduler - Optimasi scheduler disk'),
            ('5', '🚀 Preload Optimization - Percepat loading aplikasi'),
            ('0', '🔙 Kembali ke Menu Utama')
        ]
        
        menu_args = ['--title', 'Performance Tweaks',
                    '--menu', 'Pilih optimasi performa yang ingin diterapkan:',
                    '15', '75', '6']
        
        for item, desc in menu_items:
            menu_args.extend([item, desc])
        
        success, choice = self.dialog_cmd(*menu_args)
        
        if success and choice:
            choice = choice.strip()
            if choice == '1':
                self.confirm_and_run_tweak(
                    "Optimasi CPU Governor",
                    "Mengubah CPU governor ke mode performance untuk performa maksimal.",
                    self.tweaks.optimize_cpu_governor
                )
            elif choice == '2':
                self.confirm_and_run_tweak(
                    "Tuning Memory",
                    "Mengoptimasi parameter memory sistem.",
                    self.tweaks.tune_memory
                )
            elif choice == '3':
                self.confirm_and_run_tweak(
                    "Disable Unnecessary Services",
                    "Menonaktifkan service yang tidak diperlukan untuk menghemat resource.",
                    self.tweaks.disable_unnecessary_services
                )
            elif choice == '4':
                self.confirm_and_run_tweak(
                    "I/O Scheduler Optimization",
                    "Mengoptimasi I/O scheduler berdasarkan tipe disk (SSD/HDD).",
                    self.tweaks.optimize_io_scheduler
                )
            elif choice == '5':
                self.confirm_and_run_tweak(
                    "Preload Optimization",
                    "Install dan konfigurasi preload untuk mempercepat loading aplikasi.",
                    self.tweaks.optimize_preload
                )
            elif choice == '0':
                return
            
            # Kembali ke menu performance tweaks setelah menjalankan tweak
            if choice != '0':
                self.show_performance_tweaks_menu()
    
    def show_system_info(self):
        """Tampilkan informasi sistem lengkap"""
        # Show loading dialog
        subprocess.Popen(['dialog', '--title', 'System Info', 
                         '--infobox', 'Mengumpulkan informasi sistem...', '3', '40'])
        
        info = self.tweaks.get_system_info()
        
        # Format informasi sistem
        system_text = "INFORMASI SISTEM MX LINUX\n\n"
        
        system_text += "=== CPU INFORMATION ===\n"
        for key, value in info['cpu'].items():
            system_text += f"{key}: {value}\n"
        
        system_text += "\n=== MEMORY INFORMATION ===\n"
        for key, value in info['memory'].items():
            system_text += f"{key}: {value}\n"
        
        system_text += "\n=== DISK INFORMATION ===\n"
        for disk in info['disk']:
            system_text += f"Device: {disk['device']}\n"
            system_text += f"  Size: {disk['size']}, Used: {disk['used']}, Free: {disk['free']}, Usage: {disk['usage']}\n"
        
        # Tampilkan informasi dalam scrollbox
        self.dialog_cmd(
            '--title', 'Informasi Sistem Lengkap',
            '--scrolltext', system_text,
            '20', '80'
        )
    
    def confirm_and_run_tweak(self, title, description, tweak_function):
        """Konfirmasi dan jalankan tweak"""
        # Dialog konfirmasi
        success, _ = self.dialog_cmd(
            '--title', f'Konfirmasi - {title}',
            '--yesno', f'{description}\n\nLanjutkan?',
            '10', '60'
        )
        
        if success:
            # Show progress
            subprocess.Popen(['dialog', '--title', title, 
                             '--infobox', f'Menjalankan {title}...\nMohon tunggu...', '5', '50'])
            
            try:
                # Jalankan tweak dalam capture output mode untuk TUI
                # Redirect console output agar tidak mengganggu dialog
                original_stdout = sys.stdout
                original_stderr = sys.stderr
                
                with open('/tmp/mx-tweaks-output.txt', 'w') as f:
                    sys.stdout = f
                    sys.stderr = f
                    
                    # Jalankan tweak function
                    tweak_function()
                
                # Restore output
                sys.stdout = original_stdout
                sys.stderr = original_stderr
                
                # Baca hasil output
                try:
                    with open('/tmp/mx-tweaks-output.txt', 'r') as f:
                        output = f.read()
                except:
                    output = "Tweak selesai dijalankan."
                
                # Show result
                self.dialog_cmd(
                    '--title', f'{title} - Selesai',
                    '--msgbox', f'{title} telah selesai dijalankan.\n\nCek log untuk detail lengkap.',
                    '8', '60'
                )
                
            except Exception as e:
                self.logger.error(f"Error running tweak {title}: {e}")
                self.dialog_cmd(
                    '--title', f'{title} - Error',
                    '--msgbox', f'Terjadi error saat menjalankan {title}:\n{e}',
                    '8', '60'
                )
    
    def run(self):
        """Jalankan TUI interface utama"""
        # Clear screen
        os.system('clear')
        
        # Show welcome screen
        self.show_welcome()
        
        # Main loop
        while True:
            choice = self.show_main_menu()
            
            if not choice or choice == '0':
                # Dialog goodbye
                self.dialog_cmd(
                    '--title', 'MX Tweaks Pro',
                    '--msgbox', 'Terima kasih telah menggunakan MX Tweaks Pro!\n\nDibuat dengan \u2764\ufe0f untuk komunitas MX Linux.',
                    '8', '50'
                )
                break
            elif choice == '1':
                self.show_system_tweaks_menu()
            elif choice in ['2', '3', '5', '6', '7']:
                self.dialog_cmd(
                    '--title', 'Coming Soon',
                    '--msgbox', 'Fitur ini sedang dalam pengembangan.\nStay tuned untuk update selanjutnya!',
                    '6', '50'
                )
            elif choice == '4':
                self.show_performance_tweaks_menu()
            elif choice == '8':
                self.show_system_info()