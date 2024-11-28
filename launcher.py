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
from ttkthemes import ThemedTk
from PIL import Image, ImageTk
import customtkinter as ctk
import psutil
import random
import colorsys

class AnimatedBackground:
    def __init__(self, parent, colors):
        self.parent = parent
        self.colors = colors
        self.canvas = tk.Canvas(parent, highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        
        self.width = parent.winfo_screenwidth()
        self.height = parent.winfo_screenheight()
        
        self.particles = []
        self.create_particles()
        self.animate_particles()

    def create_particles(self):
        for _ in range(50):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            size = random.randint(1, 5)
            speed = random.uniform(0.5, 2)
            color = random.choice(self.colors)
            particle = {
                'x': x, 'y': y, 
                'size': size, 
                'speed': speed, 
                'color': color
            }
            self.particles.append(particle)

    def animate_particles(self):
        self.canvas.delete('all')
        for particle in self.particles:
            particle['y'] += particle['speed']
            if particle['y'] > self.height:
                particle['y'] = 0
                particle['x'] = random.randint(0, self.width)
            
            self.canvas.create_oval(
                particle['x'], particle['y'], 
                particle['x'] + particle['size'], 
                particle['y'] + particle['size'], 
                fill=particle['color'], 
                outline=''
            )
        
        self.parent.after(50, self.animate_particles)

class GradientBackground:
    def __init__(self, parent, start_color, end_color):
        self.parent = parent
        self.canvas = tk.Canvas(parent, highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        
        self.width = parent.winfo_screenwidth()
        self.height = parent.winfo_screenheight()
        
        self.start_color = self.hex_to_rgb(start_color)
        self.end_color = self.hex_to_rgb(end_color)
        
        self.create_gradient()

    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def interpolate_color(self, color1, color2, factor):
        recip = 1 - factor
        return (
            int(color1[0] * recip + color2[0] * factor),
            int(color1[1] * recip + color2[1] * factor),
            int(color1[2] * recip + color2[2] * factor)
        )

    def rgb_to_hex(self, rgb):
        return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])

    def create_gradient(self):
        for y in range(self.height):
            factor = y / self.height
            color = self.interpolate_color(self.start_color, self.end_color, factor)
            hex_color = self.rgb_to_hex(color)
            self.canvas.create_line(0, y, self.width, y, fill=hex_color)

class AIAssistantGUI:
    def __init__(self):
        # Initialize with CustomTkinter
        self.root = ctk.CTk()
        self.root.title("🤖 Integrated AI Assistant")
        self.root.geometry("1200x800")
        
        # Set theme and colors
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.colors = {
            'primary': "#1f538d",
            'secondary': "#14375e",
            'accent': "#00a8e8",
            'text': "#ffffff",
            'text_secondary': "#a0a0a0",
            'success': "#00b894",
            'warning': "#fdcb6e",
            'error': "#d63031",
            'bg_dark': "#1e1e1e",
            'bg_medium': "#2d2d2d",
            'bg_light': "#363636"
        }
        
        # Create animated background
        self.background_frame = tk.Frame(self.root)
        self.background_frame.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Choose background style
        background_styles = [
            lambda: AnimatedBackground(self.background_frame, 
                [self.colors['primary'], self.colors['secondary'], self.colors['accent']]),
            lambda: GradientBackground(self.background_frame, 
                self.colors['bg_dark'], self.colors['bg_medium'])
        ]
        random.choice(background_styles)()
        
        # Configure grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Create main container with blur effect
        self.main_container = ctk.CTkFrame(
            self.root, 
            fg_color=self.colors['bg_dark'],  
            corner_radius=20,
            bg_color='transparent'
        )
        self.main_container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(1, weight=1)
        
        # Hover and click animations
        self.add_hover_animations()
        
        # Create header
        self.create_header()
        
        # Create content area
        self.create_content_area()
        
        # Create footer
        self.create_footer()
        
        # Initialize assistant components
        self.initialize_assistant()
        
        # Add typing animation to messages
        self.setup_typing_animation()

    def add_hover_animations(self):
        def add_hover_effect(widget):
            def on_enter(e):
                widget.configure(fg_color=self.colors['secondary'])
            
            def on_leave(e):
                widget.configure(fg_color='transparent')
            
            widget.bind('<Enter>', on_enter)
            widget.bind('<Leave>', on_leave)
        
        # Add hover effects to buttons and interactive elements
        hover_widgets = [
            widget for widget in self.root.winfo_children() 
            if isinstance(widget, (ctk.CTkButton, ctk.CTkFrame))
        ]
        
        for widget in hover_widgets:
            add_hover_effect(widget)

    def setup_typing_animation(self):
        def typing_effect(text, speed=50):
            for i in range(1, len(text) + 1):
                partial_text = text[:i]
                self.messages_area.delete('1.0', 'end')
                self.messages_area.insert('end', partial_text)
                self.root.update()
                self.root.after(speed)
        
        self.typing_effect = typing_effect

    def add_message(self, sender, message):
        timestamp = datetime.datetime.now().strftime("%H:%M")
        full_message = f"\n[{timestamp}] {sender}: {message}\n"
        self.messages_area.insert('end', full_message)
        
        # Apply typing animation
        self.typing_effect(full_message)
        
        self.messages_area.see('end')

    def create_header(self):
        # Header frame with subtle animation
        header = ctk.CTkFrame(self.main_container, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        # Pulsating title effect
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left")
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="Integrated AI Assistant",
            font=("Segoe UI", 24, "bold"),
            text_color=self.colors['text']
        )
        title_label.pack(side="left", padx=10)
        
        # Pulsating animation for title
        def pulsate_label():
            current_size = 24
            def animate():
                nonlocal current_size
                current_size = 26 if current_size == 24 else 24
                title_label.configure(font=("Segoe UI", current_size, "bold"))
                self.root.after(1000, animate)
            animate()
        
        pulsate_label()
        
        # Status indicator with breathing effect
        self.status_frame = ctk.CTkFrame(header, fg_color=self.colors['bg_medium'])
        self.status_frame.pack(side="right", padx=10)
        
        self.status_indicator = ctk.CTkLabel(
            self.status_frame,
            text="●",
            font=("Segoe UI", 16),
            text_color=self.colors['success']
        )
        self.status_indicator.pack(side="left", padx=5)
        
        # Breathing effect for status indicator
        def breathing_effect():
            current_opacity = 1.0
            increasing = False
            def animate():
                nonlocal current_opacity, increasing
                
                if increasing:
                    current_opacity += 0.1
                    if current_opacity >= 1.0:
                        increasing = False
                else:
                    current_opacity -= 0.1
                    if current_opacity <= 0.5:
                        increasing = True
                
                self.status_indicator.configure(text_color=self.hex_with_alpha(self.colors['success'], current_opacity))
                self.root.after(100, animate)
            
            animate()
        
        breathing_effect()
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Active",
            font=("Segoe UI", 12),
            text_color=self.colors['text']
        )
        self.status_label.pack(side="left", padx=5)

    def hex_with_alpha(self, hex_color, alpha):
        # Convert hex to RGB with alpha
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        # Simulate alpha by blending with background
        bg_color = tuple(int(self.colors['bg_dark'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        
        blended_color = tuple(
            int(rgb[i] * alpha + bg_color[i] * (1 - alpha)) for i in range(3)
        )
        
        return '#{:02x}{:02x}{:02x}'.format(*blended_color)

    def create_content_area(self):
        # Content frame
        content = ctk.CTkFrame(self.main_container, fg_color=self.colors['bg_medium'])
        content.grid(row=1, column=0, sticky="nsew")
        content.grid_columnconfigure(0, weight=3)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)
        
        # Chat area
        self.create_chat_area(content)
        
        # Sidebar
        self.create_sidebar(content)

    def create_chat_area(self, parent):
        chat_frame = ctk.CTkFrame(parent, fg_color=self.colors['bg_light'])
        chat_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        chat_frame.grid_rowconfigure(0, weight=1)
        chat_frame.grid_columnconfigure(0, weight=1)
        
        # Messages area
        self.messages_area = ctk.CTkTextbox(
            chat_frame,
            font=("Segoe UI", 12),
            fg_color=self.colors['bg_light'],
            text_color=self.colors['text'],
            wrap="word"
        )
        self.messages_area.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 5))
        
        # Input area
        input_frame = ctk.CTkFrame(chat_frame, fg_color="transparent")
        input_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(5, 10))
        input_frame.grid_columnconfigure(0, weight=1)
        
        self.input_field = ctk.CTkEntry(
            input_frame,
            placeholder_text="Type your message here...",
            font=("Segoe UI", 12),
            height=40
        )
        self.input_field.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        send_button = ctk.CTkButton(
            input_frame,
            text="Send",
            font=("Segoe UI", 12),
            width=100,
            height=40,
            command=self.send_message
        )
        send_button.grid(row=0, column=1)
        
        mic_button = ctk.CTkButton(
            input_frame,
            text="🎤",
            font=("Segoe UI", 16),
            width=60,
            height=40,
            command=self.toggle_voice
        )
        mic_button.grid(row=0, column=2, padx=(10, 0))

    def create_sidebar(self, parent):
        sidebar = ctk.CTkFrame(parent, fg_color=self.colors['bg_light'])
        sidebar.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        # Settings button
        settings_btn = ctk.CTkButton(
            sidebar,
            text="⚙️ Settings",
            font=("Segoe UI", 12),
            command=self.open_settings
        )
        settings_btn.pack(fill="x", padx=10, pady=10)
        
        # Features list
        features_label = ctk.CTkLabel(
            sidebar,
            text="Features",
            font=("Segoe UI", 14, "bold"),
            text_color=self.colors['text']
        )
        features_label.pack(padx=10, pady=(20, 10))
        
        features = [
            "🗣️ Voice Commands",
            "🤖 AI Chat",
            "📊 Data Analysis",
            "🔍 Smart Search",
            "⚡ System Control",
            "🌐 Web Integration"
        ]
        
        for feature in features:
            feature_btn = ctk.CTkButton(
                sidebar,
                text=feature,
                font=("Segoe UI", 12),
                fg_color="transparent",
                hover_color=self.colors['bg_medium'],
                anchor="w"
            )
            feature_btn.pack(fill="x", padx=10, pady=2)
        
        # System stats
        stats_frame = ctk.CTkFrame(sidebar, fg_color=self.colors['bg_medium'])
        stats_frame.pack(fill="x", padx=10, pady=20)
        
        stats_label = ctk.CTkLabel(
            stats_frame,
            text="System Stats",
            font=("Segoe UI", 12, "bold"),
            text_color=self.colors['text']
        )
        stats_label.pack(padx=10, pady=5)
        
        self.cpu_label = ctk.CTkLabel(
            stats_frame,
            text="CPU: 0%",
            font=("Segoe UI", 10),
            text_color=self.colors['text_secondary']
        )
        self.cpu_label.pack(padx=10, pady=2)
        
        self.memory_label = ctk.CTkLabel(
            stats_frame,
            text="Memory: 0%",
            font=("Segoe UI", 10),
            text_color=self.colors['text_secondary']
        )
        self.memory_label.pack(padx=10, pady=2)

    def create_footer(self):
        footer = ctk.CTkFrame(self.main_container, fg_color="transparent")
        footer.grid(row=2, column=0, sticky="ew", pady=(20, 0))
        
        # Version info
        version_label = ctk.CTkLabel(
            footer,
            text="v2.0.0",
            font=("Segoe UI", 10),
            text_color=self.colors['text_secondary']
        )
        version_label.pack(side="left")
        
        # Status message
        self.status_message = ctk.CTkLabel(
            footer,
            text="Ready",
            font=("Segoe UI", 10),
            text_color=self.colors['text_secondary']
        )
        self.status_message.pack(side="right")

    def initialize_assistant(self):
        # Initialize AI and other components
        try:
            self.ai = AIIntegration()
            self.settings = SettingsManager()
            self.update_status("AI Assistant initialized successfully", "success")
        except Exception as e:
            self.update_status(f"Error initializing AI: {str(e)}", "error")

    def send_message(self):
        message = self.input_field.get()
        if message:
            self.add_message("You", message)
            self.input_field.delete(0, 'end')
            threading.Thread(target=self.process_message, args=(message,)).start()

    def process_message(self, message):
        try:
            response = self.ai.process_message(message)
            self.add_message("Assistant", response)
        except Exception as e:
            self.update_status(f"Error processing message: {str(e)}", "error")

    def toggle_voice(self):
        # Toggle voice recognition
        pass

    def open_settings(self):
        # Open settings dialog
        pass

    def update_status(self, message, status_type="info"):
        colors = {
            "success": self.colors['success'],
            "error": self.colors['error'],
            "warning": self.colors['warning'],
            "info": self.colors['text_secondary']
        }
        self.status_message.configure(text=message, text_color=colors.get(status_type, self.colors['text']))

    def run(self):
        self.root.mainloop()

def main():
    app = AIAssistantGUI()
    app.run()

if __name__ == "__main__":
    main()
