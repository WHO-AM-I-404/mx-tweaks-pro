#!/usr/bin/env python3
"""
Security Tweaks for MX Tweaks Pro v2.1
System hardening and security enhancements
"""

import os
import subprocess
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.prompt import Confirm, Prompt, IntPrompt
from rich.panel import Panel
from rich.table import Table
from rich import box

class SecurityTweaks:
    """System security hardening and protection"""
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.console = Console()
    
    def execute_command(self, command: str, description: str, check_success: bool = True) -> bool:
        """Execute command with security logging"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task(description, total=None)
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                progress.update(task, completed=100)
            
            if result.returncode == 0 or not check_success:
                self.console.print(f"[green]✅ {description} completed[/green]")
                self.logger.info(f"Security command executed: {command}")
                return True
            else:
                self.console.print(f"[red]❌ {description} failed: {result.stderr}[/red]")
                self.logger.error(f"Security command failed: {command} - {result.stderr}")
                return False
        except Exception as e:
            self.console.print(f"[red]❌ Error: {e}[/red]")
            self.logger.error(f"Security command error: {e}")
            return False
    
    def configure_automatic_updates(self) -> bool:
        """Configure automatic security updates"""
        self.console.print("\n[bold cyan]🔄 Configuring Automatic Security Updates[/bold cyan]")
        
        # Install unattended-upgrades
        if not self.execute_command(
            "sudo apt-get install -y unattended-upgrades apt-listchanges",
            "Installing automatic update packages"
        ):
            return False
        
        # Configure unattended-upgrades
        unattended_config = '''Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}";
    "${distro_id}:${distro_codename}-security";
    "${distro_id}ESMApps:${distro_codename}-apps-security";
    "${distro_id}ESM:${distro_codename}-infra-security";
};

Unattended-Upgrade::Package-Blacklist {
};

Unattended-Upgrade::DevRelease "false";
Unattended-Upgrade::Remove-Unused-Kernel-Packages "true";
Unattended-Upgrade::Remove-New-Unused-Dependencies "true";
Unattended-Upgrade::Remove-Unused-Dependencies "false";
Unattended-Upgrade::Automatic-Reboot "false";
Unattended-Upgrade::Automatic-Reboot-WithUsers "false";
Unattended-Upgrade::Automatic-Reboot-Time "02:00";
'''
        
        try:
            config_path = "/etc/apt/apt.conf.d/50unattended-upgrades"
            write_cmd = f"echo '{unattended_config}' | sudo tee {config_path} > /dev/null"
            
            if self.execute_command(write_cmd, "Configuring automatic updates"):
                # Enable the service
                enable_cmd = "sudo systemctl enable --now unattended-upgrades"
                return self.execute_command(enable_cmd, "Enabling automatic updates service")
        
        except Exception as e:
            self.console.print(f"[red]❌ Failed to configure automatic updates: {e}[/red]")
        
        return False
    
    def harden_ssh_configuration(self) -> bool:
        """Harden SSH server configuration"""
        self.console.print("\n[bold cyan]🔐 Hardening SSH Configuration[/bold cyan]")
        
        ssh_config_path = Path('/etc/ssh/sshd_config')
        if not ssh_config_path.exists():
            self.console.print("[yellow]⚠️ SSH server not installed, skipping SSH hardening[/yellow]")
            return True
        
        # Backup original SSH config
        backup_cmd = "sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup-mx-tweaks"
        if not self.execute_command(backup_cmd, "Backing up SSH configuration"):
            return False
        
        # SSH hardening settings
        ssh_hardening = [
            "# MX Tweaks Pro SSH Hardening",
            "Port 22",
            "Protocol 2",
            "HostKey /etc/ssh/ssh_host_rsa_key",
            "HostKey /etc/ssh/ssh_host_ecdsa_key",
            "HostKey /etc/ssh/ssh_host_ed25519_key",
            "UsePrivilegeSeparation yes",
            "KeyRegenerationInterval 3600",
            "ServerKeyBits 2048",
            "SyslogFacility AUTH",
            "LogLevel INFO",
            "LoginGraceTime 120",
            "PermitRootLogin no",
            "StrictModes yes",
            "RSAAuthentication yes",
            "PubkeyAuthentication yes",
            "IgnoreRhosts yes",
            "RhostsRSAAuthentication no",
            "HostbasedAuthentication no",
            "PermitEmptyPasswords no",
            "ChallengeResponseAuthentication no",
            "PasswordAuthentication yes",
            "X11Forwarding no",
            "X11DisplayOffset 10",
            "PrintMotd no",
            "PrintLastLog yes",
            "TCPKeepAlive yes",
            "MaxStartups 10:30:60",
            "MaxAuthTries 3",
            "ClientAliveInterval 300",
            "ClientAliveCountMax 2",
            "UseDNS no",
            "Compression delayed",
            "Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com,aes128-gcm@openssh.com,aes256-ctr,aes192-ctr,aes128-ctr",
            "MACs hmac-sha2-256-etm@openssh.com,hmac-sha2-512-etm@openssh.com,hmac-sha2-256,hmac-sha2-512",
            "KexAlgorithms curve25519-sha256@libssh.org,ecdh-sha2-nistp521,ecdh-sha2-nistp384,ecdh-sha2-nistp256,diffie-hellman-group16-sha512,diffie-hellman-group18-sha512,diffie-hellman-group14-sha256"
        ]
        
        ssh_config_content = "\n".join(ssh_hardening)
        
        try:
            write_cmd = f"echo '{ssh_config_content}' | sudo tee /etc/ssh/sshd_config > /dev/null"
            if self.execute_command(write_cmd, "Writing hardened SSH configuration"):
                # Test configuration
                test_cmd = "sudo sshd -t"
                if self.execute_command(test_cmd, "Testing SSH configuration"):
                    # Restart SSH service
                    restart_cmd = "sudo systemctl restart sshd"
                    return self.execute_command(restart_cmd, "Restarting SSH service")
                else:
                    # Restore backup on failure
                    restore_cmd = "sudo cp /etc/ssh/sshd_config.backup-mx-tweaks /etc/ssh/sshd_config"
                    self.execute_command(restore_cmd, "Restoring SSH configuration")
                    return False
        
        except Exception as e:
            self.console.print(f"[red]❌ SSH hardening failed: {e}[/red]")
        
        return False
    
    def configure_firewall_rules(self) -> bool:
        """Configure comprehensive firewall rules"""
        self.console.print("\n[bold cyan]🔥 Configuring Advanced Firewall Rules[/bold cyan]")
        
        # Check if UFW is available
        ufw_check = subprocess.run(['which', 'ufw'], capture_output=True)
        if ufw_check.returncode != 0:
            # Install UFW
            if not self.execute_command("sudo apt-get install -y ufw", "Installing UFW firewall"):
                return False
        
        # Reset UFW to defaults
        self.execute_command("sudo ufw --force reset", "Resetting firewall rules")
        
        # Default policies
        firewall_rules = [
            "sudo ufw default deny incoming",
            "sudo ufw default allow outgoing",
            "sudo ufw default deny forward"
        ]
        
        # Essential services
        essential_rules = [
            "sudo ufw allow 22/tcp comment 'SSH'",
            "sudo ufw allow 80/tcp comment 'HTTP'",
            "sudo ufw allow 443/tcp comment 'HTTPS'"
        ]
        
        # Security rules
        security_rules = [
            "sudo ufw limit ssh comment 'Rate limit SSH'",
            "sudo ufw deny 135,139,445/tcp comment 'Block SMB'",
            "sudo ufw deny 137,138/udp comment 'Block NetBIOS'",
            "sudo ufw logging on"
        ]
        
        all_rules = firewall_rules + essential_rules + security_rules
        success_count = 0
        
        for rule in all_rules:
            if self.execute_command(rule, f"Applying firewall rule", check_success=False):
                success_count += 1
        
        # Enable firewall
        if self.execute_command("sudo ufw --force enable", "Enabling firewall"):
            success_count += 1
        
        self.console.print(f"[green]✅ Applied {success_count}/{len(all_rules) + 1} firewall rules[/green]")
        return success_count > len(all_rules) // 2
    
    def setup_fail2ban(self) -> bool:
        """Setup Fail2Ban for intrusion prevention"""
        self.console.print("\n[bold cyan]🛡️ Setting up Fail2Ban Intrusion Prevention[/bold cyan]")
        
        # Install Fail2Ban
        if not self.execute_command("sudo apt-get install -y fail2ban", "Installing Fail2Ban"):
            return False
        
        # Fail2Ban jail configuration
        jail_config = '''[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3
backend = auto
usedns = warn
logencoding = auto
enabled = false
mode = normal
filter = %(__name__)s
destemail = root@localhost
sender = root@localhost
mta = sendmail
protocol = tcp
chain = <known/chain>
port = 0:65535
fail2ban_agent = Fail2Ban/%(fail2ban_version)s
banaction = ufw
banaction_allports = ufw
action_abuseipdb = abuseipdb
action = %(action_)s

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600

[apache-auth]
enabled = true
port = http,https
filter = apache-auth
logpath = /var/log/apache*/*error.log
maxretry = 3

[apache-badbots]
enabled = true
port = http,https
filter = apache-badbots
logpath = /var/log/apache*/*access.log
bantime = 86400
maxretry = 1

[apache-noscript]
enabled = true
port = http,https
filter = apache-noscript
logpath = /var/log/apache*/*access.log
maxretry = 3

[apache-overflows]
enabled = true
port = http,https
filter = apache-overflows
logpath = /var/log/apache*/*error.log
maxretry = 2
'''
        
        try:
            jail_file = "/etc/fail2ban/jail.local"
            write_cmd = f"echo '{jail_config}' | sudo tee {jail_file} > /dev/null"
            
            if self.execute_command(write_cmd, "Writing Fail2Ban configuration"):
                # Start and enable Fail2Ban
                start_cmd = "sudo systemctl enable --now fail2ban"
                if self.execute_command(start_cmd, "Starting Fail2Ban service"):
                    # Check status
                    status_cmd = "sudo fail2ban-client status"
                    return self.execute_command(status_cmd, "Checking Fail2Ban status", check_success=False)
        
        except Exception as e:
            self.console.print(f"[red]❌ Fail2Ban setup failed: {e}[/red]")
        
        return False
    
    def secure_kernel_parameters(self) -> bool:
        """Configure secure kernel parameters"""
        self.console.print("\n[bold cyan]⚙️ Configuring Secure Kernel Parameters[/bold cyan]")
        
        kernel_security = [
            # Network security
            ("net.ipv4.conf.all.send_redirects", "0", "Disable ICMP redirects"),
            ("net.ipv4.conf.default.send_redirects", "0", "Disable ICMP redirects (default)"),
            ("net.ipv4.conf.all.accept_redirects", "0", "Don't accept ICMP redirects"),
            ("net.ipv4.conf.default.accept_redirects", "0", "Don't accept ICMP redirects (default)"),
            ("net.ipv6.conf.all.accept_redirects", "0", "Don't accept IPv6 ICMP redirects"),
            ("net.ipv4.conf.all.secure_redirects", "0", "Don't accept secure ICMP redirects"),
            ("net.ipv4.conf.default.secure_redirects", "0", "Don't accept secure ICMP redirects (default)"),
            ("net.ipv4.conf.all.accept_source_route", "0", "Don't accept source routing"),
            ("net.ipv4.conf.default.accept_source_route", "0", "Don't accept source routing (default)"),
            ("net.ipv6.conf.all.accept_source_route", "0", "Don't accept IPv6 source routing"),
            ("net.ipv4.conf.all.log_martians", "1", "Log martian packets"),
            ("net.ipv4.conf.default.log_martians", "1", "Log martian packets (default)"),
            ("net.ipv4.icmp_echo_ignore_broadcasts", "1", "Ignore ICMP ping broadcasts"),
            ("net.ipv4.icmp_ignore_bogus_error_responses", "1", "Ignore bogus ICMP responses"),
            ("net.ipv4.ip_forward", "0", "Disable IP forwarding"),
            ("net.ipv6.conf.all.forwarding", "0", "Disable IPv6 forwarding"),
            
            # Memory security
            ("kernel.dmesg_restrict", "1", "Restrict dmesg access"),
            ("kernel.kptr_restrict", "2", "Restrict kernel pointer access"),
            ("kernel.yama.ptrace_scope", "1", "Restrict ptrace scope"),
            
            # File system security
            ("fs.suid_dumpable", "0", "Disable core dumps for setuid programs"),
            ("fs.protected_hardlinks", "1", "Enable protected hardlinks"),
            ("fs.protected_symlinks", "1", "Enable protected symlinks"),
            
            # Process security
            ("kernel.exec-shield", "1", "Enable exec-shield (if available)"),
            ("kernel.randomize_va_space", "2", "Full ASLR"),
        ]
        
        success_count = 0
        applied_params = []
        
        for param, value, description in kernel_security:
            command = f"echo '{value}' | sudo tee /proc/sys/{param.replace('.', '/')} > /dev/null 2>/dev/null || true"
            if self.execute_command(command, description, check_success=False):
                success_count += 1
                applied_params.append((param, value))
        
        # Make changes permanent
        if applied_params:
            self._make_kernel_params_permanent(applied_params)
        
        self.console.print(f"[green]✅ Applied {success_count}/{len(kernel_security)} kernel security parameters[/green]")
        return success_count > len(kernel_security) // 2
    
    def _make_kernel_params_permanent(self, params: List[Tuple[str, str]]):
        """Make kernel parameters permanent"""
        try:
            sysctl_file = "/etc/sysctl.d/99-mx-tweaks-security.conf"
            
            header = [
                "# MX Tweaks Pro v2.1 - Security Hardening",
                f"# Generated on {time.strftime('%Y-%m-%d %H:%M:%S')}",
                "# Kernel security parameters",
                ""
            ]
            
            content_lines = header + [f"{param}={value}" for param, value in params]
            content = "\n".join(content_lines)
            
            write_cmd = f"echo '{content}' | sudo tee {sysctl_file} > /dev/null"
            if self.execute_command(write_cmd, "Making security parameters permanent"):
                apply_cmd = f"sudo sysctl -p {sysctl_file}"
                self.execute_command(apply_cmd, "Applying permanent security settings")
        
        except Exception as e:
            self.logger.error(f"Failed to make security parameters permanent: {e}")
    
    def audit_system_security(self) -> Dict:
        """Perform comprehensive security audit"""
        self.console.print("\n[bold cyan]🔍 Performing Security Audit[/bold cyan]")
        
        audit_results = {
            "timestamp": time.time(),
            "user_accounts": self._audit_user_accounts(),
            "file_permissions": self._audit_file_permissions(),
            "services": self._audit_services(),
            "network_security": self._audit_network_security(),
            "updates": self._audit_system_updates()
        }
        
        return audit_results
    
    def _audit_user_accounts(self) -> Dict:
        """Audit user account security"""
        try:
            # Check for accounts with empty passwords
            passwd_result = subprocess.run(['sudo', 'awk', '-F:', '($2 == "") {print $1}', '/etc/shadow'],
                                         capture_output=True, text=True)
            empty_passwords = passwd_result.stdout.strip().split('\n') if passwd_result.stdout.strip() else []
            
            # Check for UID 0 accounts (should only be root)
            uid0_result = subprocess.run(['awk', '-F:', '($3 == 0) {print $1}', '/etc/passwd'],
                                       capture_output=True, text=True)
            uid0_accounts = uid0_result.stdout.strip().split('\n') if uid0_result.stdout.strip() else []
            
            return {
                "empty_passwords": empty_passwords,
                "uid0_accounts": uid0_accounts,
                "issues": len(empty_passwords) + max(0, len(uid0_accounts) - 1)  # root is expected
            }
        except Exception as e:
            self.logger.error(f"User account audit failed: {e}")
            return {"error": str(e)}
    
    def _audit_file_permissions(self) -> Dict:
        """Audit critical file permissions"""
        critical_files = {
            "/etc/passwd": "644",
            "/etc/shadow": "640",
            "/etc/group": "644",
            "/etc/gshadow": "640",
            "/etc/ssh/sshd_config": "600"
        }
        
        issues = []
        
        for file_path, expected_perms in critical_files.items():
            try:
                if os.path.exists(file_path):
                    stat_info = os.stat(file_path)
                    actual_perms = oct(stat_info.st_mode)[-3:]
                    if actual_perms != expected_perms:
                        issues.append({
                            "file": file_path,
                            "expected": expected_perms,
                            "actual": actual_perms
                        })
            except Exception as e:
                issues.append({
                    "file": file_path,
                    "error": str(e)
                })
        
        return {"issues": issues, "files_checked": len(critical_files)}
    
    def _audit_services(self) -> Dict:
        """Audit running services"""
        try:
            # Get running services
            services_result = subprocess.run(
                ['systemctl', 'list-units', '--type=service', '--state=active', '--no-pager'],
                capture_output=True, text=True
            )
            
            running_services = []
            if services_result.returncode == 0:
                lines = services_result.stdout.split('\n')[1:-6]  # Skip header and footer
                for line in lines:
                    if line.strip():
                        parts = line.split()
                        if len(parts) > 0:
                            running_services.append(parts[0])
            
            # Potentially risky services
            risky_services = ['telnet', 'rsh', 'rlogin', 'vsftpd', 'ftpd']
            found_risky = [service for service in risky_services if any(service in rs for rs in running_services)]
            
            return {
                "total_running": len(running_services),
                "risky_services": found_risky,
                "issues": len(found_risky)
            }
        
        except Exception as e:
            self.logger.error(f"Service audit failed: {e}")
            return {"error": str(e)}
    
    def _audit_network_security(self) -> Dict:
        """Audit network security settings"""
        network_checks = {
            "ip_forwarding": "/proc/sys/net/ipv4/ip_forward",
            "icmp_redirects": "/proc/sys/net/ipv4/conf/all/accept_redirects",
            "source_routing": "/proc/sys/net/ipv4/conf/all/accept_source_route"
        }
        
        issues = []
        
        for check_name, file_path in network_checks.items():
            try:
                with open(file_path, 'r') as f:
                    value = f.read().strip()
                    if value != "0":
                        issues.append({
                            "check": check_name,
                            "file": file_path,
                            "value": value,
                            "expected": "0"
                        })
            except Exception as e:
                issues.append({
                    "check": check_name,
                    "error": str(e)
                })
        
        return {"issues": issues, "checks_performed": len(network_checks)}
    
    def _audit_system_updates(self) -> Dict:
        """Check for available security updates"""
        try:
            # Update package lists
            subprocess.run(['sudo', 'apt-get', 'update'], capture_output=True)
            
            # Check for security updates
            upgrade_result = subprocess.run(
                ['apt', 'list', '--upgradable'],
                capture_output=True, text=True
            )
            
            total_updates = 0
            security_updates = 0
            
            if upgrade_result.returncode == 0:
                lines = upgrade_result.stdout.split('\n')
                for line in lines[1:]:  # Skip header
                    if line.strip():
                        total_updates += 1
                        if 'security' in line.lower():
                            security_updates += 1
            
            return {
                "total_updates": total_updates,
                "security_updates": security_updates,
                "update_needed": total_updates > 0
            }
        
        except Exception as e:
            self.logger.error(f"Update audit failed: {e}")
            return {"error": str(e)}
    
    def run_comprehensive_security_hardening(self) -> Dict:
        """Run comprehensive security hardening suite"""
        self.console.print(Panel(
            "[bold cyan]MX Tweaks Pro v2.1 - Security Hardening Suite[/bold cyan]\n"
            "This will harden your system security with industry best practices.\n"
            "[yellow]Warning: Some changes may affect system functionality.[/yellow]",
            title="🛡️ Security Hardening",
            border_style="bright_red"
        ))
        
        # Run security audit first
        self.console.print("\n[bold yellow]🔍 Running Security Audit[/bold yellow]")
        audit_before = self.audit_system_security()
        
        results = {
            "timestamp": time.time(),
            "audit_before": audit_before,
            "hardening_applied": [],
            "audit_after": {}
        }
        
        # Security hardening modules
        hardening_modules = [
            ("Automatic Updates", self.configure_automatic_updates),
            ("SSH Hardening", self.harden_ssh_configuration),
            ("Firewall Rules", self.configure_firewall_rules),
            ("Fail2Ban", self.setup_fail2ban),
            ("Kernel Security", self.secure_kernel_parameters)
        ]
        
        success_count = 0
        
        for name, hardening_func in hardening_modules:
            if Confirm.ask(f"\n[yellow]Apply {name}?[/yellow]"):
                try:
                    if hardening_func():
                        results["hardening_applied"].append(name)
                        success_count += 1
                        self.console.print(f"[green]✅ {name} applied successfully[/green]")
                    else:
                        self.console.print(f"[yellow]⚠️ {name} partially applied or skipped[/yellow]")
                except Exception as e:
                    self.logger.error(f"Error in {name}: {e}")
                    self.console.print(f"[red]❌ {name} failed: {e}[/red]")
        
        # Run security audit after hardening
        if success_count > 0:
            self.console.print("\n[bold yellow]🔍 Running Post-Hardening Audit[/bold yellow]")
            results["audit_after"] = self.audit_system_security()
        
        # Display results
        self._display_security_results(results)
        
        results["success_rate"] = success_count / len(hardening_modules)
        return results
    
    def _display_security_results(self, results: Dict):
        """Display comprehensive security results"""
        self.console.print("\n" + "="*60)
        self.console.print("[bold green]🛡️ SECURITY HARDENING RESULTS[/bold green]")
        self.console.print("="*60)
        
        # Summary table
        summary_table = Table(title="Security Hardening Summary", box=box.ROUNDED)
        summary_table.add_column("Component", style="cyan")
        summary_table.add_column("Status", style="green")
        summary_table.add_column("Impact", style="yellow")
        
        hardening_impacts = {
            "Automatic Updates": "High - Keeps system secure",
            "SSH Hardening": "High - Prevents unauthorized access",
            "Firewall Rules": "High - Blocks malicious traffic",
            "Fail2Ban": "Medium - Prevents brute force attacks",
            "Kernel Security": "Medium - Hardens kernel parameters"
        }
        
        for component in hardening_impacts:
            status = "✅ Applied" if component in results["hardening_applied"] else "❌ Not Applied"
            impact = hardening_impacts[component]
            summary_table.add_row(component, status, impact)
        
        self.console.print(summary_table)
        
        # Security score
        applied_count = len(results["hardening_applied"])
        total_count = len(hardening_impacts)
        security_score = (applied_count / total_count) * 100
        
        score_color = "green" if security_score >= 80 else "yellow" if security_score >= 60 else "red"
        self.console.print(f"\n[bold {score_color}]Security Score: {security_score:.1f}%[/bold {score_color}]")
        
        # Recommendations
        if security_score < 100:
            self.console.print("\n[bold yellow]Recommendations:[/bold yellow]")
            for component in hardening_impacts:
                if component not in results["hardening_applied"]:
                    self.console.print(f"[yellow]- Apply {component} for better security[/yellow]")
        
        self.console.print(f"\n[dim]Security hardening completed. Applied {applied_count}/{total_count} security measures.[/dim]")