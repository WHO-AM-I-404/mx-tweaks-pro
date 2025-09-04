# MX Tweaks Pro v2.1

## 🚀 Advanced System Optimization Utility for MX Linux

**MX Tweaks Pro** is an advanced tweaking utility designed specifically for MX Linux. This application provides comprehensive system optimization, security hardening, network tuning, and appearance customization in one integrated platform with CLI, TUI, and GUI interfaces.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MX Linux](https://img.shields.io/badge/MX%20Linux-19.x+-green.svg)](https://mxlinux.org/)

---

## ✨ Key Features

### 🖥️ **Multiple Interface Options**
- **CLI Mode**: Command Line Interface with Rich library formatting
- **TUI Mode**: Terminal User Interface with interactive dialogs
- **GUI Mode**: Graphical User Interface built with tkinter

### 🔧 **System Tweaks**
- Disable swap for SSD optimization
- Clean package cache and temporary files
- Optimize boot time by disabling unnecessary services
- Automatically fix broken packages
- Advanced system profiling and benchmarking

### 🚀 **Performance Optimization**
- CPU Governor management (performance/powersave modes)
- Memory tuning with swappiness optimization
- I/O Scheduler optimization based on disk type
- Preload installation for faster application loading
- Real-time performance monitoring

### 🎨 **Appearance Tweaks**
- Automatic dark/light theme application
- Font rendering optimization with anti-aliasing
- Desktop compositor configuration
- Panel transparency settings
- Icon theme installation
- Automated wallpaper slideshows

### 🌐 **Network Optimization**
- TCP stack optimization with BBR congestion control
- DNS resolution optimization with fast DNS servers
- Network buffer tuning for better performance
- WiFi power management optimization
- Firewall configuration with UFW
- Network benchmark tools

### 🔒 **Security Hardening**
- SSH server hardening with modern ciphers
- Automatic security updates configuration
- Fail2Ban intrusion prevention setup
- Kernel security parameter tuning
- Comprehensive security audit tools
- Advanced firewall rules management

### 💾 **Backup & Restore System**
- Automated backup scheduling (daily/weekly/custom intervals)
- Selective backup options (config/home/system files)
- Incremental backup support
- Backup integrity verification
- Easy restore functionality
- Cloud backup integration ready

### 🔌 **Plugin Architecture**
- Modular plugin system for extensibility
- Hot-swappable plugins without restart
- Plugin dependency management
- Custom plugin development API
- Built-in plugin manager

---

## 📋 System Requirements

### **Minimum Requirements:**
- **OS**: MX Linux 19.x or newer
- **RAM**: 1 GB (2 GB recommended)
- **Storage**: 100 MB free space
- **Python**: Python 3.8+
- **Privileges**: sudo access for system tweaks

### **Dependencies:**
```bash
# Core dependencies
python3 >= 3.8
python3-pip
sudo access

# Python packages (auto-installed)
rich >= 13.0.0
click >= 8.0.0
psutil >= 5.8.0
configparser
schedule

# Optional GUI dependencies
python3-tk  # for GUI mode

# System packages
ufw          # for firewall management
fail2ban     # for intrusion prevention
dialog       # for TUI mode
```

---

## 🔧 Installation

### **Method 1: Quick Install (Recommended)**
```bash
# Download and install
curl -fsSL https://raw.githubusercontent.com/your-repo/mx-tweaks-pro/main/install.sh | bash

# Or manual download
wget -O install.sh https://raw.githubusercontent.com/your-repo/mx-tweaks-pro/main/install.sh
chmod +x install.sh
./install.sh
```

### **Method 2: Manual Installation**
```bash
# Clone repository
git clone https://github.com/your-repo/mx-tweaks-pro.git
cd mx-tweaks-pro

# Install dependencies
sudo apt update
sudo apt install python3 python3-pip python3-tk dialog ufw

# Install Python packages
pip3 install -r requirements.txt

# Make executable
chmod +x mx-tweaks-pro
sudo ln -sf $(pwd)/mx-tweaks-pro /usr/local/bin/mx-tweaks-pro
```

### **Method 3: Development Installation**
```bash
# Clone with development branch
git clone -b development https://github.com/your-repo/mx-tweaks-pro.git
cd mx-tweaks-pro

# Setup development environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt

# Install in development mode
pip install -e .
```

---

## 🚀 Usage Guide

### **Basic Usage**
```bash
# Launch with default interface (CLI)
mx-tweaks-pro

# Specific interface modes
mx-tweaks-pro --cli      # Command Line Interface
mx-tweaks-pro --tui      # Terminal User Interface 
mx-tweaks-pro --gui      # Graphical User Interface

# Debug mode
mx-tweaks-pro --debug

# Show help
mx-tweaks-pro --help
```

### **CLI Mode Commands**
```bash
# System optimization
mx-tweaks-pro system --optimize
mx-tweaks-pro system --cleanup
mx-tweaks-pro system --benchmark

# Performance tweaks
mx-tweaks-pro performance --cpu-governor performance
mx-tweaks-pro performance --memory-tune
mx-tweaks-pro performance --io-optimize

# Network optimization
mx-tweaks-pro network --optimize-tcp
mx-tweaks-pro network --dns-optimize
mx-tweaks-pro network --benchmark

# Security hardening
mx-tweaks-pro security --harden-ssh
mx-tweaks-pro security --setup-firewall
mx-tweaks-pro security --audit

# Appearance tweaks
mx-tweaks-pro appearance --dark-theme
mx-tweaks-pro appearance --optimize-fonts
mx-tweaks-pro appearance --transparency 80

# Backup operations
mx-tweaks-pro backup --create "my-backup"
mx-tweaks-pro backup --schedule daily
mx-tweaks-pro backup --list

# Plugin management
mx-tweaks-pro plugins --list
mx-tweaks-pro plugins --load custom-plugin
mx-tweaks-pro plugins --install /path/to/plugin
```

### **Configuration**
```bash
# Configuration locations
~/.mx-tweaks-pro/config.ini    # Main configuration
~/.mx-tweaks-pro/backups/      # Backup settings
~/.mx-tweaks-pro/plugins/      # Plugin directory
~/.mx-tweaks-pro/logs/         # Log files
```

### **Example Configuration (config.ini)**
```ini
[general]
interface = cli
debug = false
backup_before_tweaks = true

[system]
auto_cleanup = true
optimize_boot = true
swap_management = auto

[performance] 
cpu_governor = performance
swappiness = 10
io_scheduler = mq-deadline

[network]
tcp_optimization = true
dns_servers = 1.1.1.1,8.8.8.8
firewall_enabled = true

[security]
ssh_hardening = true
auto_updates = true
fail2ban_enabled = true

[appearance]
theme = dark
font_optimization = true
panel_transparency = 80

[backup]
schedule = daily
time = 02:00
include_home = false
include_system = true
compression = gzip
retention_days = 30

[plugins]
auto_load = monitoring,themes
disabled = 
```

---

## 🎯 Feature Documentation

### **System Tweaks**

#### **Disable Swap**
- Temporarily disable swap for better SSD performance
- Permanent disable with automatic `/etc/fstab` backup
- Configurable swap management policies

#### **Package Cache Cleanup**
- APT cache cleanup and optimization
- Orphaned package removal
- Automatic cleanup scheduling

#### **Boot Time Optimization**
- Analyze boot performance with systemd-analyze
- Disable unnecessary services based on system analysis
- Service conflict detection and resolution

### **Performance Optimization**

#### **CPU Governor Management**
- Dynamic CPU frequency scaling control
- Performance vs power saving modes
- Per-core governor configuration support

#### **Memory Optimization**
- Swappiness tuning (recommended: 10 for desktop)
- Cache pressure adjustment
- Dirty page ratio optimization for better I/O performance

#### **I/O Scheduler Optimization**
- Automatic detection of SSD vs HDD
- Optimal scheduler selection (mq-deadline for SSD, BFQ for HDD)
- Custom scheduler parameters tuning

### **Network Optimization**

#### **TCP Stack Optimization**
- BBR congestion control for better performance
- TCP window scaling and timestamps
- Buffer size optimization for high-bandwidth connections

#### **DNS Optimization**
- Fast DNS server configuration (Cloudflare, Google)
- DNS caching and timeout optimization
- Performance testing and monitoring

### **Security Hardening**

#### **SSH Hardening**
- Disable root login and weak authentication
- Modern cipher suites only
- Rate limiting and connection restrictions

#### **Firewall Configuration**
- UFW-based firewall setup with sensible defaults
- Service-specific rules (SSH, HTTP, HTTPS)
- Rate limiting for SSH connections

#### **Fail2Ban Integration**
- Brute force protection for SSH and web services
- Configurable ban times and retry limits
- Comprehensive monitoring and alerting

---

## 🔌 Plugin Development

### **Creating a Custom Plugin**

```python
#!/usr/bin/env python3
"""
Custom Plugin for MX Tweaks Pro
"""

from src.plugin_system import PluginInterface
from typing import Dict, Any, Callable

class MyCustomPlugin(PluginInterface):
    @property
    def name(self) -> str:
        return "My Custom Plugin"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "A custom plugin example"
    
    def initialize(self) -> bool:
        self.logger.info(f"Initializing {self.name}")
        return True
    
    def execute(self, *args, **kwargs) -> Any:
        self.console.print(f"[green]Executing {self.name}[/green]")
        return {"status": "success", "message": "Plugin executed successfully"}
    
    def get_commands(self) -> Dict[str, Callable]:
        return {
            "hello": self.hello_command,
            "config": self.config_command
        }
    
    def hello_command(self, name: str = "World"):
        self.console.print(f"[cyan]Hello, {name}![/cyan]")
        return f"Hello, {name}!"
```

### **Plugin Installation**
```bash
# Install plugin
mx-tweaks-pro plugins --install ~/.mx-tweaks-pro/plugins/my-plugin

# Load and execute
mx-tweaks-pro plugins --load my-plugin
mx-tweaks-pro plugins --execute "my-plugin.hello" --args "MX Linux"
```

---

## 🐛 Troubleshooting

### **Common Issues**

#### **Permission Denied Errors**
```bash
# Ensure user is in sudo group
sudo usermod -aG sudo $USER
newgrp sudo

# Check sudo access
sudo -l
```

#### **Python Dependencies Issues**
```bash
# Update pip
python3 -m pip install --upgrade pip

# Install with user flag
pip3 install --user rich click psutil configparser schedule

# Fix missing tkinter
sudo apt install python3-tk
```

#### **GUI Mode Not Working**
```bash
# Install GUI dependencies
sudo apt install python3-tk

# Test tkinter
python3 -c "import tkinter; tkinter.Tk().mainloop()"
```

### **Debug Mode**
```bash
# Enable debug logging
mx-tweaks-pro --debug

# Check log files
tail -f ~/.mx-tweaks-pro/logs/mx-tweaks.log

# Reset configuration
mx-tweaks-pro config --reset --confirm
```

---

## 🚀 Advanced Usage

### **Automation Scripts**

#### **Complete System Optimization**
```bash
#!/bin/bash
# complete-optimization.sh

echo "Starting complete MX Linux optimization..."

# System tweaks
mx-tweaks-pro system --cleanup
mx-tweaks-pro system --optimize-boot
mx-tweaks-pro system --fix-packages

# Performance optimization
mx-tweaks-pro performance --cpu-governor performance
mx-tweaks-pro performance --memory-tune
mx-tweaks-pro performance --io-optimize

# Network optimization
mx-tweaks-pro network --optimize-tcp
mx-tweaks-pro network --dns-optimize

# Security hardening
mx-tweaks-pro security --harden-ssh
mx-tweaks-pro security --setup-firewall

# Create backup
mx-tweaks-pro backup --create "post-optimization-$(date +%Y%m%d)"

echo "Optimization complete! Please reboot for all changes to take effect."
```

### **Systemd Integration**
```ini
# /etc/systemd/system/mx-tweaks-monitor.service
[Unit]
Description=MX Tweaks Pro System Monitor
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/local/bin/mx-tweaks-pro monitor --daemon
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### **Cron Automation**
```bash
# Add to crontab (crontab -e)
# Daily cleanup at 3 AM
0 3 * * * /usr/local/bin/mx-tweaks-pro system --cleanup --quiet

# Weekly maintenance on Sunday at 2 AM
0 2 * * 0 /usr/local/bin/mx-tweaks-pro maintenance --weekly

# Backup every 6 hours
0 */6 * * * /usr/local/bin/mx-tweaks-pro backup --create "auto-$(date +%Y%m%d-%H%M)"
```

---

## 🤝 Contributing

### **Development Setup**
```bash
# Fork and clone repository
git clone https://github.com/YOUR_USERNAME/mx-tweaks-pro.git
cd mx-tweaks-pro

# Create development branch
git checkout -b feature/your-feature-name

# Setup development environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
python -m pytest tests/
```

### **Code Style Guidelines**
- Use type hints for all functions
- Follow PEP 8 style guidelines
- Write comprehensive docstrings
- Use Rich console for user output
- Implement proper error handling
- Write unit tests for new features

### **Testing**
```bash
# Run all tests
python -m pytest

# Coverage report
python -m pytest --cov=src --cov-report=html

# Performance testing
python -m pytest tests/performance/ --benchmark-only
```

### **Pull Request Process**
1. Fork the repository
2. Create a feature branch
3. Make changes with comprehensive tests
4. Ensure all tests pass
5. Update documentation
6. Submit pull request
7. Address code review feedback
8. Merge after approval

---

## 📄 License

**MX Tweaks Pro** is licensed under the **MIT License**. See [LICENSE](LICENSE) file for details.

---

## 🌟 Changelog

### **v2.1.0** (Latest)

#### ✨ **New Features:**
- Complete GUI Mode with tkinter interface
- Advanced Backup System with automated scheduling
- Plugin Architecture for extensibility
- Appearance Tweaks for desktop customization
- Network Optimization suite
- Security Hardening toolkit
- Real-time System Monitoring
- Built-in Benchmark Engine

#### 🔧 **Improvements:**
- Enhanced CLI interface with rich formatting
- Better error handling and logging
- Improved configuration management
- Advanced system profiling capabilities
- Plugin hot-swapping support

#### 🐛 **Bug Fixes:**
- Fixed memory optimization edge cases
- Resolved GUI responsiveness issues
- Improved backup integrity verification
- Enhanced plugin dependency resolution

### **v2.0.0**
- Complete rewrite with modular architecture
- Multiple interface support (CLI/TUI/GUI)
- Advanced system optimization toolkit
- Performance monitoring and benchmarking
- Backup and restore functionality

### **v1.0.0**
- Initial release with basic system tweaks
- CLI interface support
- Configuration management
- MX Linux optimization tools

---

## 📞 Support & Community

### **Getting Help**
- 📚 **Documentation**: [GitHub Wiki](https://github.com/WHO-AM-I-404/mx-tweaks-pro/wiki)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/WHO-AM-I-404/mx-tweaks-pro/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/WHO-AM-I-404/mx-tweaks-pro/discussions)
- 📧 **Email**: mxtweaks@gmail.com

### **Community**
- 🌐 **MX Linux Forum**: [MX Linux Community](https://mxlinux.org/forum)
- 💬 **Discord**: [Join our Discord](https://discord.gg/mx-tweaks-pro)
- 🐦 **Twitter**: [@MXTweaksPro](https://twitter.com/MXTweaksPro)

---

## 🙏 Acknowledgments

### **Special Thanks:**
- **MX Linux Team** - For creating an excellent Linux distribution
- **Python Community** - For amazing libraries and tools
- **Contributors** - All developers who contributed to this project
- **Beta Testers** - Community members who helped test and improve

### **Libraries Used:**
- [Rich](https://github.com/Textualize/rich) - Terminal formatting
- [Click](https://github.com/pallets/click) - Command line interfaces
- [psutil](https://github.com/giampaolo/psutil) - System monitoring
- [schedule](https://github.com/dbader/schedule) - Task scheduling

---

## 📋 Quick Reference

```bash
# Quick Start Commands
mx-tweaks-pro                    # Launch default interface
mx-tweaks-pro --gui             # Launch GUI mode
mx-tweaks-pro system --optimize # Quick system optimization
mx-tweaks-pro backup --create   # Create backup
mx-tweaks-pro plugins --list    # List available plugins

# Configuration Files
~/.mx-tweaks-pro/config.ini     # Main configuration
~/.mx-tweaks-pro/backups/       # Backup storage
~/.mx-tweaks-pro/plugins/       # Plugin directory
~/.mx-tweaks-pro/logs/          # Log files

# Support
GitHub: https://github.com/your-repo/mx-tweaks-pro
Email: support@mx-tweaks-pro.com
Documentation: https://mx-tweaks-pro.readthedocs.io
```

---

**Made with ❤️ for the MX Linux Community**

*Optimize your MX Linux experience with MX Tweaks Pro v2.1 - The Ultimate System Optimization Tool*

**Happy Optimizing! 🚀**
