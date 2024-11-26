from typing import List, Dict, Any
import json
from datetime import datetime
import os

class MemoryManager:
    def __init__(self, max_memory: int = 10):
        self.max_memory = max_memory
        self.conversation_history = []
        self.context_data = {}
        # Use absolute path for memory file
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.data_dir = os.path.join(base_dir, "data")
        os.makedirs(self.data_dir, exist_ok=True)
        self.memory_file = os.path.join(self.data_dir, "conversation_memory.json")
        self.load_memory()

    def add_interaction(self, user_input: str, assistant_response: str, metadata: Dict[str, Any] = None):
        """Add a new interaction to the conversation history"""
        interaction = {
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'assistant_response': assistant_response,
            'metadata': metadata or {}
        }
        
        self.conversation_history.append(interaction)
        
        # Keep only the last max_memory interactions
        if len(self.conversation_history) > self.max_memory:
            self.conversation_history = self.conversation_history[-self.max_memory:]
        
        self.save_memory()

    def get_recent_context(self, n: int = 3) -> List[Dict[str, Any]]:
        """Get the n most recent interactions"""
        return self.conversation_history[-n:]

    def add_context_data(self, key: str, value: Any):
        """Add persistent context data"""
        self.context_data[key] = value
        self.save_memory()

    def get_context_data(self, key: str) -> Any:
        """Retrieve context data"""
        return self.context_data.get(key)

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        self.save_memory()

    def save_memory(self):
        """Save conversation history to file"""
        memory_data = {
            'conversation_history': self.conversation_history,
            'context_data': self.context_data
        }
        try:
            with open(self.memory_file, 'w') as f:
                json.dump(memory_data, f, indent=2)
        except Exception as e:
            print(f"Error saving memory: {e}")

    def load_memory(self):
        """Load conversation history from file"""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r') as f:
                    memory_data = json.load(f)
                    self.conversation_history = memory_data.get('conversation_history', [])
                    self.context_data = memory_data.get('context_data', {})
        except Exception as e:
            print(f"Error loading memory: {e}")

    def get_formatted_history(self) -> str:
        """Get formatted conversation history for AI context"""
        formatted = "Previous conversation context:\n"
        for interaction in self.conversation_history[-3:]:  # Last 3 interactions
            formatted += f"\nUser: {interaction['user_input']}\n"
            formatted += f"Assistant: {interaction['assistant_response']}\n"
        return formatted
