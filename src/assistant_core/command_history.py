from typing import List, Dict, Optional
from datetime import datetime
import json
import os

class CommandHistory:
    def __init__(self, history_file: str = "command_history.json"):
        self.history_file = history_file
        self.history: List[Dict] = []
        self.load_history()
        
    def load_history(self):
        """Load command history from file"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    self.history = json.load(f)
        except Exception as e:
            print(f"Error loading history: {e}")
            self.history = []
            
    def save_history(self):
        """Save command history to file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")
            
    def add_command(self, command: str, args: List[str], status: str, result: str):
        """Add a command to history"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "command": command,
            "args": args,
            "status": status,
            "result": result
        }
        self.history.append(entry)
        self.save_history()
        
    def get_last_command(self) -> Optional[Dict]:
        """Get the last executed command"""
        return self.history[-1] if self.history else None
        
    def get_command_history(self, limit: int = 10) -> List[Dict]:
        """Get recent command history"""
        return self.history[-limit:]
        
    def search_history(self, query: str) -> List[Dict]:
        """Search command history"""
        query = query.lower()
        return [
            entry for entry in self.history
            if query in entry["command"].lower() or
            any(query in arg.lower() for arg in entry["args"])
        ]
        
    def get_successful_commands(self) -> List[Dict]:
        """Get list of successful commands"""
        return [
            entry for entry in self.history
            if entry["status"] == "success"
        ]
        
    def get_failed_commands(self) -> List[Dict]:
        """Get list of failed commands"""
        return [
            entry for entry in self.history
            if entry["status"] == "error"
        ]
        
    def clear_history(self):
        """Clear command history"""
        self.history = []
        self.save_history()
