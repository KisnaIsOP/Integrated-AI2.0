from typing import Dict, Any, List
import os
import psutil
import subprocess
from .command_history import CommandHistory

class SystemController:
    def __init__(self):
        self.command_history = CommandHistory()
        self.common_apps = {
            'notepad': 'notepad.exe',
            'calculator': 'calc.exe',
            'paint': 'mspaint.exe',
            'explorer': 'explorer.exe',
            'browser': 'msedge.exe',
            'word': 'winword.exe',
            'excel': 'excel.exe',
            'terminal': 'cmd.exe'
        }

    def execute_command(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a system command"""
        try:
            if not isinstance(command_data, dict):
                return {"status": "error", "message": "Invalid command format"}
                
            command = command_data.get('command', '').lower()
            args = command_data.get('args', [])
            
            # Handle application launch commands
            if command == 'open':
                if not args:
                    return {"status": "error", "message": "No application specified"}
                app_name = ' '.join(args).lower()
                result = self.open_application(app_name)
                self.command_history.add_command(command, args, result.get('status', 'error'), result.get('message', ''))
                return result
            
            # Handle system commands
            elif command == 'system':
                result = self.get_system_info()
                self.command_history.add_command(command, args, "success", str(result))
                return result
            
            error_msg = f"Unknown command: {command}"
            self.command_history.add_command(command, args, "error", error_msg)
            return {'status': 'error', 'message': error_msg}
            
        except Exception as e:
            error_msg = f"Error executing {command}: {str(e)}"
            self.command_history.add_command(command, args, "error", error_msg)
            return {'status': 'error', 'message': error_msg}

    def open_application(self, app_name):
        """Open a specified application"""
        try:
            # Clean up app name
            app_name = app_name.lower().strip()
            
            # Check if it's a common app
            if app_name in self.common_apps:
                app_path = self.common_apps[app_name]
            else:
                # Try to find the executable
                possible_exes = [
                    f"{app_name}.exe",
                    os.path.join(os.environ.get('ProgramFiles', ''), f"{app_name}.exe"),
                    os.path.join(os.environ.get('ProgramFiles(x86)', ''), f"{app_name}.exe")
                ]
                
                app_path = None
                for exe in possible_exes:
                    if os.path.exists(exe):
                        app_path = exe
                        break
            
            if app_path and os.path.exists(app_path):
                subprocess.Popen(app_path)
                return {"status": "success", "message": f"Successfully opened {app_name}"}
            else:
                return {"status": "error", "message": f"Could not find application: {app_name}"}
                
        except Exception as e:
            return {"status": "error", "message": f"Error opening {app_name}: {str(e)}"}

    def get_system_info(self):
        """Get system information"""
        try:
            return {
                "status": "success",
                "cpu_usage": psutil.cpu_percent(),
                "memory_used": psutil.virtual_memory().percent,
                "disk_used": psutil.disk_usage('/').percent,
                "system": platform.system(),
                "version": platform.version()
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_command_history(self, limit: int = 10) -> List[Dict]:
        """Get recent command history"""
        return self.command_history.get_command_history(limit)
        
    def search_command_history(self, query: str) -> List[Dict]:
        """Search command history"""
        return self.command_history.search_history(query)
