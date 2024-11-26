import os
import subprocess
import json
import psutil
import winreg
from typing import Dict, List, Optional, Tuple
import logging
from pathlib import Path

class AppManager:
    def __init__(self):
        self.app_registry = {}
        self.running_processes = {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize app registry
        self.load_app_registry()
        self.scan_installed_apps()
        
    def load_app_registry(self):
        """Load application registry from file"""
        registry_path = "app_registry.json"
        try:
            if os.path.exists(registry_path):
                with open(registry_path, 'r') as f:
                    self.app_registry = json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading app registry: {e}")
            
    def save_app_registry(self):
        """Save application registry to file"""
        try:
            with open("app_registry.json", 'w') as f:
                json.dump(self.app_registry, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving app registry: {e}")
            
    def scan_installed_apps(self):
        """Scan Windows registry for installed applications"""
        try:
            paths = [
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths",
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
            ]
            
            for path in paths:
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path) as key:
                        self._scan_registry_key(key)
                except WindowsError:
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error scanning installed apps: {e}")
            
    def _scan_registry_key(self, key):
        """Scan a registry key for applications"""
        try:
            i = 0
            while True:
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    with winreg.OpenKey(key, subkey_name) as subkey:
                        try:
                            path = winreg.QueryValue(subkey, None)
                            if path and path.endswith('.exe'):
                                name = os.path.splitext(os.path.basename(path))[0]
                                self.register_app(name.lower(), path)
                        except WindowsError:
                            pass
                    i += 1
                except WindowsError:
                    break
        except Exception as e:
            self.logger.error(f"Error scanning registry key: {e}")
            
    def register_app(self, name: str, path: str, aliases: List[str] = None):
        """Register an application with the manager"""
        if not os.path.exists(path):
            return False
            
        self.app_registry[name] = {
            "path": path,
            "aliases": aliases or [],
            "last_used": None
        }
        self.save_app_registry()
        return True
        
    def find_app(self, query: str) -> Optional[str]:
        """Find application path by name or alias"""
        query = query.lower()
        
        # Direct match
        if query in self.app_registry:
            return self.app_registry[query]["path"]
            
        # Check aliases
        for name, info in self.app_registry.items():
            if query in info.get("aliases", []):
                return info["path"]
                
        # Partial match
        for name, info in self.app_registry.items():
            if query in name.lower():
                return info["path"]
                
        return None
        
    def launch_app(self, app_name: str) -> Tuple[bool, str]:
        """Launch an application"""
        try:
            app_path = self.find_app(app_name)
            if not app_path:
                return False, f"Application '{app_name}' not found"
                
            process = subprocess.Popen(
                [app_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            self.running_processes[app_name] = process
            self.update_last_used(app_name)
            
            return True, f"Launched {app_name}"
            
        except Exception as e:
            error_msg = f"Error launching {app_name}: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
            
    def close_app(self, app_name: str) -> Tuple[bool, str]:
        """Close an application"""
        try:
            # Check running processes first
            if app_name in self.running_processes:
                process = self.running_processes[app_name]
                process.terminate()
                return True, f"Closed {app_name}"
                
            # Try to find by name
            for proc in psutil.process_iter(['name']):
                try:
                    if app_name.lower() in proc.info['name'].lower():
                        proc.terminate()
                        return True, f"Closed {app_name}"
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
            return False, f"Application '{app_name}' not found running"
            
        except Exception as e:
            error_msg = f"Error closing {app_name}: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
            
    def update_last_used(self, app_name: str):
        """Update last used timestamp for an app"""
        if app_name in self.app_registry:
            self.app_registry[app_name]["last_used"] = time.time()
            self.save_app_registry()
            
    def get_running_apps(self) -> List[str]:
        """Get list of running applications"""
        running_apps = []
        for proc in psutil.process_iter(['name']):
            try:
                running_apps.append(proc.info['name'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return running_apps
        
    def get_system_info(self) -> Dict:
        """Get system resource information"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu_usage": cpu_percent,
                "memory_used": memory.percent,
                "disk_used": disk.percent,
                "running_apps": len(self.get_running_apps())
            }
        except Exception as e:
            self.logger.error(f"Error getting system info: {e}")
            return {}
            
    def cleanup(self):
        """Cleanup resources"""
        try:
            # Terminate any processes we started
            for process in self.running_processes.values():
                try:
                    process.terminate()
                except:
                    pass
            self.save_app_registry()
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            
    def __del__(self):
        """Cleanup on destruction"""
        self.cleanup()
