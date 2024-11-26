import asyncio
import sys
import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from src.assistant_core.ai_integration import AIIntegration
from src.assistant_core.settings_manager import SettingsManager
from dotenv import load_dotenv
import threading
import json
import datetime

class AIAssistantGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 Integrated AI Assistant")
        self.root.geometry("1200x800")
        
        # Set theme colors
        self.colors = {
            'bg': '#1E1E1E',            # Dark background
            'secondary_bg': '#252526',   # Slightly lighter background
            'accent': '#007ACC',         # Blue accent
            'text': '#D4D4D4',          # Light gray text
            'input_bg': '#2D2D2D',      # Input background
            'success': '#4EC9B0',       # Success color
            'error': '#F44747',         # Error color
            'button_hover': '#005999'   # Button hover color
        }
        
        # Configure root window
        self.root.configure(bg=self.colors['bg'])
        
        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure custom styles
        self.style.configure(
            'Custom.TFrame',
            background=self.colors['bg']
        )
        self.style.configure(
            'Header.TLabel',
            background=self.colors['bg'],
            foreground=self.colors['text'],
            font=('Segoe UI', 12, 'bold')
        )
        self.style.configure(
            'Custom.TButton',
            background=self.colors['accent'],
            foreground=self.colors['text'],
            padding=10,
            font=('Segoe UI', 10)
        )
        self.style.map(
            'Custom.TButton',
            background=[('active', self.colors['button_hover'])]
        )
        
        self.setup_gui()
        self.initialize_ai()
        
    def setup_gui(self):
        # Main container
        self.main_frame = ttk.Frame(self.root, style='Custom.TFrame', padding="20")
        self.main_frame.grid(row=0, column=0, sticky='nsew')
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Header frame
        header_frame = ttk.Frame(self.main_frame, style='Custom.TFrame')
        header_frame.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0, 20))
        
        # Title
        ttk.Label(
            header_frame,
            text="🤖 Integrated AI Assistant",
            style='Header.TLabel'
        ).pack(side=tk.LEFT)
        
        # Model selection
        model_frame = ttk.Frame(header_frame, style='Custom.TFrame')
        model_frame.pack(side=tk.RIGHT)
        
        ttk.Label(
            model_frame,
            text="AI Model:",
            style='Header.TLabel'
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.model_var = tk.StringVar(value="auto")
        models = ["auto", "gpt-4", "gpt-3.5-turbo", "gemini-pro"]
        model_menu = ttk.OptionMenu(
            model_frame,
            self.model_var,
            "auto",
            *models
        )
        model_menu.pack(side=tk.LEFT)
        
        # Chat display
        self.chat_frame = ttk.Frame(self.main_frame, style='Custom.TFrame')
        self.chat_frame.grid(row=1, column=0, columnspan=2, sticky='nsew', pady=(0, 20))
        self.chat_frame.columnconfigure(0, weight=1)
        self.chat_frame.rowconfigure(0, weight=1)
        
        self.chat_display = scrolledtext.ScrolledText(
            self.chat_frame,
            wrap=tk.WORD,
            font=('Cascadia Code', 10),
            bg=self.colors['input_bg'],
            fg=self.colors['text'],
            insertbackground=self.colors['text'],
            selectbackground=self.colors['accent'],
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.chat_display.grid(row=0, column=0, sticky='nsew')
        self.chat_display.config(state=tk.DISABLED)
        
        # Configure chat display tags
        self.chat_display.tag_configure('user', foreground='#569CD6', font=('Cascadia Code', 10, 'bold'))
        self.chat_display.tag_configure('assistant', foreground='#4EC9B0', font=('Cascadia Code', 10, 'bold'))
        self.chat_display.tag_configure('system', foreground='#CE9178', font=('Cascadia Code', 10, 'bold'))
        self.chat_display.tag_configure('error', foreground='#F44747', font=('Cascadia Code', 10, 'bold'))
        
        # Input area
        input_frame = ttk.Frame(self.main_frame, style='Custom.TFrame')
        input_frame.grid(row=2, column=0, columnspan=2, sticky='ew')
        input_frame.columnconfigure(0, weight=1)
        
        self.input_field = tk.Text(
            input_frame,
            wrap=tk.WORD,
            height=4,
            font=('Cascadia Code', 10),
            bg=self.colors['input_bg'],
            fg=self.colors['text'],
            insertbackground=self.colors['text'],
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.input_field.grid(row=0, column=0, sticky='ew', padx=(0, 10))
        self.input_field.bind('<Control-Return>', lambda e: self.send_message())
        
        # Buttons frame
        button_frame = ttk.Frame(input_frame, style='Custom.TFrame')
        button_frame.grid(row=0, column=1)
        
        # Send button with icon
        send_button = ttk.Button(
            button_frame,
            text="Send 📤",
            command=self.send_message,
            style='Custom.TButton'
        )
        send_button.pack(pady=(0, 5))
        
        # Clear button with icon
        clear_button = ttk.Button(
            button_frame,
            text="Clear 🗑️",
            command=self.clear_chat,
            style='Custom.TButton'
        )
        clear_button.pack()
        
        # Feature buttons
        feature_frame = ttk.Frame(self.main_frame, style='Custom.TFrame')
        feature_frame.grid(row=3, column=0, columnspan=2, sticky='ew', pady=(20, 0))
        
        features = [
            ("🔧 System Commands", self.toggle_system_commands),
            ("🎤 Voice Input", self.toggle_voice_input),
            ("🌤️ Weather Info", self.get_weather),
            ("⚙️ Settings", self.open_settings)
        ]
        
        for i, (text, command) in enumerate(features):
            btn = ttk.Button(
                feature_frame,
                text=text,
                command=command,
                style='Custom.TButton'
            )
            btn.grid(row=0, column=i, padx=5)
            feature_frame.columnconfigure(i, weight=1)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(
            self.main_frame,
            textvariable=self.status_var,
            style='Header.TLabel',
            font=('Segoe UI', 9)
        )
        status_bar.grid(row=4, column=0, columnspan=2, sticky='w', pady=(10, 0))
        
        # Configure weights
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        
    def append_to_chat(self, sender, message, message_type='normal'):
        self.chat_display.config(state=tk.NORMAL)
        timestamp = datetime.datetime.now().strftime("%H:%M")
        
        if sender == "You":
            self.chat_display.insert(tk.END, f"\n[{timestamp}] ", 'system')
            self.chat_display.insert(tk.END, f"You:\n", 'user')
            self.chat_display.insert(tk.END, f"{message}\n")
        elif sender == "Assistant":
            self.chat_display.insert(tk.END, f"\n[{timestamp}] ", 'system')
            self.chat_display.insert(tk.END, f"AI Assistant:\n", 'assistant')
            if message_type == 'error':
                self.chat_display.insert(tk.END, f"{message}\n", 'error')
            else:
                self.chat_display.insert(tk.END, f"{message}\n")
        else:
            self.chat_display.insert(tk.END, f"\n[{timestamp}] ", 'system')
            self.chat_display.insert(tk.END, f"{sender}:\n", 'system')
            self.chat_display.insert(tk.END, f"{message}\n")
        
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
    def initialize_ai(self):
        try:
            load_dotenv()
            
            if not os.getenv('OPENAI_API_KEY') or not os.getenv('GEMINI_API_KEY'):
                messagebox.showerror("Error", "API keys not found. Please check your .env file.")
                return
            
            self.ai = AIIntegration()
            self.settings_manager = SettingsManager()
            
            self.system_commands_enabled = False
            self.voice_input_enabled = False
            
            self.status_var.set("AI Assistant initialized and ready")
            self.append_to_chat(
                "System",
                "🤖 Welcome to the AI Assistant!\n\n" +
                "Features available:\n" +
                "• Multi-model AI responses (select model above)\n" +
                "• System commands (toggle button below)\n" +
                "• Voice input (coming soon)\n" +
                "• Weather information\n" +
                "• Customizable settings\n\n" +
                "How can I help you today?"
            )
            
        except Exception as e:
            messagebox.showerror("Initialization Error", f"Error initializing AI: {str(e)}")
            self.status_var.set("Initialization failed")
    
    def send_message(self):
        message = self.input_field.get("1.0", tk.END).strip()
        if not message:
            return
        
        self.input_field.delete("1.0", tk.END)
        self.append_to_chat("You", message)
        self.status_var.set("Processing...")
        self.root.update_idletasks()
        
        def async_process():
            async def process():
                try:
                    response = await self.ai.multi_model_response(
                        message,
                        model_preference=self.model_var.get() if self.model_var.get() != "auto" else None,
                        system_commands_enabled=self.system_commands_enabled
                    )
                    
                    if response.get("success", False):
                        self.root.after(0, self.append_to_chat, "Assistant", response["response"])
                    else:
                        self.root.after(0, self.append_to_chat, "Assistant", 
                                      response.get("error", "Unknown error occurred"), 'error')
                        
                except Exception as e:
                    self.root.after(0, self.append_to_chat, "Assistant", f"Error: {str(e)}", 'error')
                finally:
                    self.root.after(0, self.status_var.set, "Ready")
            
            asyncio.run(process())
        
        threading.Thread(target=async_process, daemon=True).start()
    
    def clear_chat(self):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.config(state=tk.DISABLED)
        self.append_to_chat("System", "Chat cleared. How can I help you?")
    
    def toggle_system_commands(self):
        self.system_commands_enabled = not self.system_commands_enabled
        status = "enabled" if self.system_commands_enabled else "disabled"
        self.append_to_chat("System", f"🔧 System commands {status}")
    
    def toggle_voice_input(self):
        self.voice_input_enabled = not self.voice_input_enabled
        status = "enabled" if self.voice_input_enabled else "disabled"
        self.append_to_chat("System", f"🎤 Voice input {status}\nThis feature is coming soon!")
    
    def get_weather(self):
        self.append_to_chat("System", "🌤️ Getting weather information...\nType a message with a city name to get weather info!")
    
    def open_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("⚙️ Settings")
        settings_window.geometry("500x400")
        settings_window.configure(bg=self.colors['bg'])
        
        # Add settings title
        ttk.Label(
            settings_window,
            text="Settings",
            style='Header.TLabel',
            font=('Segoe UI', 14, 'bold')
        ).pack(pady=20)
        
        # Settings content placeholder
        ttk.Label(
            settings_window,
            text="Settings panel coming soon!",
            style='Header.TLabel'
        ).pack(pady=20)

def main():
    root = tk.Tk()
    app = AIAssistantGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
