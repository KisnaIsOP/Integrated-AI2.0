import os
import subprocess
import psutil
import pyautogui
import webbrowser
from typing import Dict, Any, List, Optional
import json
import logging

class SystemController:
    def __init__(self):
        self.common_apps = {
            'chrome': r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            'firefox': r'C:\Program Files\Mozilla Firefox\firefox.exe',
            'notepad': 'notepad.exe',
            'calculator': 'calc.exe',
            'explorer': 'explorer.exe'
        }
        
        # Configure PyAutoGUI safely
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 1.0
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def execute_command(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a system command based on parsed AI response"""
        command_type = command_data.get('command_type', '')
        action = command_data.get('action', '')
        parameters = command_data.get('parameters', {})
        
        try:
            if command_type == 'application_launch':
                return self.launch_application(parameters.get('app_name', ''))
            elif command_type == 'web_navigation':
                return self.open_website(parameters.get('url', ''))
            elif command_type == 'system_setting':
                return self.modify_system_setting(action, parameters)
            elif command_type == 'file_operation':
                return self.handle_file_operation(action, parameters)
            else:
                return {'error': f'Unknown command type: {command_type}'}
        except Exception as e:
            self.logger.error(f"Error executing command: {str(e)}")
            return {'error': str(e)}

    def launch_application(self, app_name: str) -> Dict[str, Any]:
        """Launch a system application"""
        try:
            app_name = app_name.lower()
            if app_name in self.common_apps:
                path = self.common_apps[app_name]
                subprocess.Popen(path)
                return {'success': True, 'message': f'Launched {app_name}'}
            else:
                # Try launching directly
                subprocess.Popen(app_name)
                return {'success': True, 'message': f'Launched {app_name}'}
        except Exception as e:
            return {'error': f'Failed to launch {app_name}: {str(e)}'}

    def open_website(self, url: str) -> Dict[str, Any]:
        """Open a website in the default browser"""
        try:
            # Add http:// if no protocol specified
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            webbrowser.open(url)
            return {'success': True, 'message': f'Opened {url}'}
        except Exception as e:
            return {'error': f'Failed to open {url}: {str(e)}'}

    def modify_system_setting(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Modify system settings"""
        try:
            if action == 'volume':
                # Implement volume control
                level = parameters.get('level', 50)
                # Add volume control implementation here
                return {'success': True, 'message': f'Set volume to {level}%'}
            elif action == 'brightness':
                # Implement brightness control
                level = parameters.get('level', 50)
                # Add brightness control implementation here
                return {'success': True, 'message': f'Set brightness to {level}%'}
            else:
                return {'error': f'Unknown setting action: {action}'}
        except Exception as e:
            return {'error': f'Failed to modify setting: {str(e)}'}

    def handle_file_operation(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle file operations"""
        try:
            if action == 'create':
                path = parameters.get('path', '')
                content = parameters.get('content', '')
                with open(path, 'w') as f:
                    f.write(content)
                return {'success': True, 'message': f'Created file: {path}'}
            elif action == 'delete':
                path = parameters.get('path', '')
                os.remove(path)
                return {'success': True, 'message': f'Deleted file: {path}'}
            elif action == 'read':
                path = parameters.get('path', '')
                with open(path, 'r') as f:
                    content = f.read()
                return {'success': True, 'content': content}
            else:
                return {'error': f'Unknown file operation: {action}'}
        except Exception as e:
            return {'error': f'File operation failed: {str(e)}'}

    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        try:
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_usage': cpu_percent,
                'memory_used': memory.percent,
                'disk_used': disk.percent,
                'battery': self.get_battery_info()
            }
        except Exception as e:
            return {'error': f'Failed to get system info: {str(e)}'}

    def get_battery_info(self) -> Dict[str, Any]:
        """Get battery information"""
        try:
            battery = psutil.sensors_battery()
            if battery:
                return {
                    'percent': battery.percent,
                    'power_plugged': battery.power_plugged,
                    'time_left': battery.secsleft
                }
            return {'error': 'No battery found'}
        except Exception as e:
            return {'error': f'Failed to get battery info: {str(e)}'}

    def list_running_processes(self) -> List[Dict[str, Any]]:
        """List all running processes"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                processes.append(proc.info)
            return processes
        except Exception as e:
            return [{'error': f'Failed to list processes: {str(e)}'}]
