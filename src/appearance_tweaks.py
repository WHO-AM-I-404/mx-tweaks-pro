#!/usr/bin/env python3
"""
Appearance Tweaks for MX Tweaks Pro v2.1
Desktop customization and visual enhancements
"""

import os
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt, IntPrompt
from rich.panel import Panel
from rich.table import Table
from rich import box

class AppearanceTweaks:
    """Desktop appearance and customization tweaks"""
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.console = Console()
        self.desktop_env = self._detect_desktop_environment()
    
    def _detect_desktop_environment(self) -> str:
        """Detect current desktop environment"""
        desktop_session = os.environ.get('DESKTOP_SESSION', '')
        xdg_current_desktop = os.environ.get('XDG_CURRENT_DESKTOP', '')
        
        if 'xfce' in desktop_session.lower() or 'xfce' in xdg_current_desktop.lower():
            return 'XFCE'
        elif 'kde' in desktop_session.lower() or 'plasma' in xdg_current_desktop.lower():
            return 'KDE'
        elif 'gnome' in desktop_session.lower() or 'gnome' in xdg_current_desktop.lower():
            return 'GNOME'
        elif 'mate' in desktop_session.lower():
            return 'MATE'
        elif 'cinnamon' in desktop_session.lower():
            return 'Cinnamon'
        else:
            return 'Unknown'
    
    def execute_command(self, command: str, description: str) -> bool:
        """Execute command with progress indicator"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task(description, total=None)
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                progress.update(task, completed=100)
            
            if result.returncode == 0:
                self.console.print(f"[green]✅ {description} completed[/green]")
                return True
            else:
                self.console.print(f"[red]❌ {description} failed: {result.stderr}[/red]")
                return False
        except Exception as e:
            self.console.print(f"[red]❌ Error: {e}[/red]")
            return False
    
    def apply_dark_theme(self) -> bool:
        """Apply system-wide dark theme"""
        self.console.print("\n[bold cyan]🌙 Applying Dark Theme[/bold cyan]")
        
        success = True
        
        if self.desktop_env == 'XFCE':
            commands = [
                "xfconf-query -c xsettings -p /Net/ThemeName -s 'Adwaita-dark'",
                "xfconf-query -c xfwm4 -p /general/theme -s 'Adwaita-dark'",
                "xfconf-query -c xsettings -p /Net/IconThemeName -s 'Adwaita'"
            ]
            for cmd in commands:
                if not self.execute_command(cmd, "Setting XFCE dark theme"):
                    success = False
        
        elif self.desktop_env == 'GNOME':
            commands = [
                "gsettings set org.gnome.desktop.interface gtk-theme 'Adwaita-dark'",
                "gsettings set org.gnome.desktop.interface color-scheme 'prefer-dark'"
            ]
            for cmd in commands:
                if not self.execute_command(cmd, "Setting GNOME dark theme"):
                    success = False
        
        elif self.desktop_env == 'KDE':
            self.console.print("[yellow]KDE theme changes require manual configuration through System Settings[/yellow]")
        
        return success
    
    def optimize_font_rendering(self) -> bool:
        """Optimize font rendering for better readability"""
        self.console.print("\n[bold cyan]🕰️ Optimizing Font Rendering[/bold cyan]")
        
        # Create fontconfig directory if it doesn't exist
        fontconfig_dir = Path.home() / '.config' / 'fontconfig'
        fontconfig_dir.mkdir(parents=True, exist_ok=True)
        
        # Font configuration for better rendering
        font_config = '''<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "fonts.dtd">
<fontconfig>
  <match target="font">
    <edit name="antialias" mode="assign">
      <bool>true</bool>
    </edit>
    <edit name="hinting" mode="assign">
      <bool>true</bool>
    </edit>
    <edit name="hintstyle" mode="assign">
      <const>hintslight</const>
    </edit>
    <edit name="rgba" mode="assign">
      <const>rgb</const>
    </edit>
    <edit name="lcdfilter" mode="assign">
      <const>lcddefault</const>
    </edit>
  </match>
</fontconfig>'''
        
        try:
            font_config_file = fontconfig_dir / 'fonts.conf'
            with open(font_config_file, 'w') as f:
                f.write(font_config)
            
            # Update font cache
            self.execute_command("fc-cache -fv", "Updating font cache")
            
            self.console.print("[green]✅ Font rendering optimized[/green]")
            return True
            
        except Exception as e:
            self.console.print(f"[red]❌ Font optimization failed: {e}[/red]")
            return False
    
    def configure_compositor(self) -> bool:
        """Configure desktop compositor for better performance"""
        self.console.print("\n[bold cyan]🎨 Configuring Compositor[/bold cyan]")
        
        if self.desktop_env == 'XFCE':
            # XFCE compositor settings
            commands = [
                "xfconf-query -c xfwm4 -p /general/use_compositing -s true",
                "xfconf-query -c xfwm4 -p /general/frame_opacity -s 90",
                "xfconf-query -c xfwm4 -p /general/inactive_opacity -s 95",
                "xfconf-query -c xfwm4 -p /general/show_frame_shadow -s true"
            ]
            
            success = True
            for cmd in commands:
                if not self.execute_command(cmd, "Configuring XFCE compositor"):
                    success = False
            
            return success
        
        else:
            self.console.print(f"[yellow]Compositor configuration not implemented for {self.desktop_env}[/yellow]")
            return True
    
    def install_icon_themes(self) -> bool:
        """Install popular icon themes"""
        self.console.print("\n[bold cyan]🎨 Installing Icon Themes[/bold cyan]")
        
        icon_themes = [
            "papirus-icon-theme",
            "numix-icon-theme",
            "adwaita-icon-theme-full"
        ]
        
        success_count = 0
        for theme in icon_themes:
            if self.execute_command(f"sudo apt-get install -y {theme}", f"Installing {theme}"):
                success_count += 1
        
        self.console.print(f"[green]✅ Installed {success_count}/{len(icon_themes)} icon themes[/green]")
        return success_count > 0
    
    def configure_panel_transparency(self, opacity: int = 80) -> bool:
        """Configure panel transparency"""
        self.console.print(f"\n[bold cyan]📊 Setting Panel Transparency to {opacity}%[/bold cyan]")
        
        if self.desktop_env == 'XFCE':
            # XFCE panel transparency
            commands = [
                f"xfconf-query -c xfce4-panel -p /panels/panel-1/background-alpha -s {opacity}",
                "xfconf-query -c xfce4-panel -p /panels/panel-1/background-style -s 1"
            ]
            
            success = True
            for cmd in commands:
                if not self.execute_command(cmd, "Setting panel transparency"):
                    success = False
            
            return success
        else:
            self.console.print(f"[yellow]Panel transparency not supported for {self.desktop_env}[/yellow]")
            return True
    
    def optimize_animations(self, enable: bool = True) -> bool:
        """Configure desktop animations for performance"""
        action = "Enabling" if enable else "Disabling"
        self.console.print(f"\n[bold cyan]✨ {action} Desktop Animations[/bold cyan]")
        
        if self.desktop_env == 'GNOME':
            animation_setting = "true" if enable else "false"
            return self.execute_command(
                f"gsettings set org.gnome.desktop.interface enable-animations {animation_setting}",
                f"{action} GNOME animations"
            )
        
        elif self.desktop_env == 'XFCE':
            # XFCE doesn't have global animation settings, but we can optimize window manager
            return self.execute_command(
                "xfconf-query -c xfwm4 -p /general/show_frame_shadow -s true",
                "Optimizing XFCE window effects"
            )
        
        else:
            self.console.print(f"[yellow]Animation settings not implemented for {self.desktop_env}[/yellow]")
            return True
    
    def configure_wallpaper_slideshow(self, interval_minutes: int = 30) -> bool:
        """Configure automatic wallpaper slideshow"""
        self.console.print(f"\n[bold cyan]🇼 Setting Wallpaper Slideshow ({interval_minutes} min intervals)[/bold cyan]")
        
        wallpaper_dir = Path.home() / 'Pictures' / 'Wallpapers'
        if not wallpaper_dir.exists():
            wallpaper_dir.mkdir(parents=True)
            self.console.print(f"[blue]Created wallpaper directory: {wallpaper_dir}[/blue]")
        
        if self.desktop_env == 'GNOME':
            # Create GNOME wallpaper slideshow XML
            slideshow_xml = f'''<background>
  <starttime>
    <year>2024</year>
    <month>01</month>
    <day>01</day>
    <hour>00</hour>
    <minute>00</minute>
    <second>00</second>
  </starttime>
  <static>
    <duration>{interval_minutes * 60}</duration>
    <file>{wallpaper_dir}</file>
  </static>
</background>'''
            
            slideshow_file = wallpaper_dir / 'slideshow.xml'
            try:
                with open(slideshow_file, 'w') as f:
                    f.write(slideshow_xml)
                
                return self.execute_command(
                    f"gsettings set org.gnome.desktop.background picture-uri file://{slideshow_file}",
                    "Setting GNOME wallpaper slideshow"
                )
            except Exception as e:
                self.console.print(f"[red]Failed to create slideshow: {e}[/red]")
                return False
        
        else:
            self.console.print(f"[yellow]Wallpaper slideshow not implemented for {self.desktop_env}[/yellow]")
            return True
    
    def run_appearance_optimization(self) -> Dict:
        """Run comprehensive appearance optimization"""
        self.console.print(Panel(
            f"[bold cyan]MX Tweaks Pro v2.1 - Appearance Optimization[/bold cyan]\n"
            f"Detected Desktop Environment: [yellow]{self.desktop_env}[/yellow]\n"
            f"This will optimize visual appearance and desktop customization.",
            title="🎨 Appearance Tweaks",
            border_style="bright_blue"
        ))
        
        # Show available tweaks
        tweaks_table = Table(title="Available Appearance Tweaks", box=box.ROUNDED)
        tweaks_table.add_column("Tweak", style="cyan")
        tweaks_table.add_column("Description", style="white")
        tweaks_table.add_column("Compatibility", style="yellow")
        
        tweaks_table.add_row(
            "Dark Theme", "Apply system-wide dark theme", 
            "XFCE, GNOME" if self.desktop_env in ['XFCE', 'GNOME'] else "Limited"
        )
        tweaks_table.add_row(
            "Font Rendering", "Optimize font anti-aliasing and hinting", "All"
        )
        tweaks_table.add_row(
            "Compositor", "Configure desktop compositor effects", 
            "XFCE" if self.desktop_env == 'XFCE' else "Limited"
        )
        tweaks_table.add_row(
            "Icon Themes", "Install popular icon themes", "All"
        )
        tweaks_table.add_row(
            "Panel Transparency", "Configure panel transparency", 
            "XFCE" if self.desktop_env == 'XFCE' else "Limited"
        )
        tweaks_table.add_row(
            "Animations", "Optimize desktop animations", "GNOME, XFCE"
        )
        
        self.console.print(tweaks_table)
        
        results = {
            "timestamp": __import__('time').time(),
            "desktop_environment": self.desktop_env,
            "tweaks_applied": [],
            "success_count": 0
        }
        
        # Interactive selection
        if Confirm.ask("\n[yellow]Apply dark theme?[/yellow]"):
            if self.apply_dark_theme():
                results["tweaks_applied"].append("Dark Theme")
                results["success_count"] += 1
        
        if Confirm.ask("[yellow]Optimize font rendering?[/yellow]"):
            if self.optimize_font_rendering():
                results["tweaks_applied"].append("Font Rendering")
                results["success_count"] += 1
        
        if Confirm.ask("[yellow]Configure compositor effects?[/yellow]"):
            if self.configure_compositor():
                results["tweaks_applied"].append("Compositor")
                results["success_count"] += 1
        
        if Confirm.ask("[yellow]Install additional icon themes?[/yellow]"):
            if self.install_icon_themes():
                results["tweaks_applied"].append("Icon Themes")
                results["success_count"] += 1
        
        if self.desktop_env == 'XFCE' and Confirm.ask("[yellow]Configure panel transparency?[/yellow]"):
            opacity = IntPrompt.ask("Enter transparency percentage (0-100)", default=80)
            if self.configure_panel_transparency(opacity):
                results["tweaks_applied"].append("Panel Transparency")
                results["success_count"] += 1
        
        if Confirm.ask("[yellow]Optimize animations?[/yellow]"):
            enable = Confirm.ask("Enable animations? (No = disable for performance)")
            if self.optimize_animations(enable):
                results["tweaks_applied"].append("Animations")
                results["success_count"] += 1
        
        # Summary
        self.console.print(Panel(
            f"[bold green]Appearance Optimization Complete![/bold green]\n\n"
            f"Applied tweaks: {results['success_count']}/{len(results['tweaks_applied']) if results['tweaks_applied'] else 'None'}\n"
            f"Optimized: {', '.join(results['tweaks_applied']) if results['tweaks_applied'] else 'None'}\n\n"
            f"[dim]Note: Some changes may require logging out and back in to take full effect.[/dim]",
            title="🎉 Results",
            border_style="green"
        ))
        
        return results