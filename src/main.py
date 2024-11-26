import os
import customtkinter as ctk
import tkinter as tk
from threading import Thread
import speech_recognition as sr
from dotenv import load_dotenv
import time
from PIL import Image, ImageTk
import asyncio
import concurrent.futures
from assistant_core.ai_integration import AIIntegration
from assistant_core.voice_manager import VoiceManager
from assistant_core.settings_manager import SettingsManager
from assistant_core.settings_dialog import SettingsDialog

# Load environment variables
load_dotenv()

class IntegratedAssistant(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AI Assistant")
        self.geometry("1000x600")
        
        # Initialize event loop
        self.loop = asyncio.new_event_loop()
        self.thread = Thread(target=self.start_background_loop, daemon=True)
        self.thread.start()
        
        # Initialize state
        self.is_processing = False
        self.message_queue = asyncio.Queue()
        
        # Initialize settings
        self.settings_manager = SettingsManager()
        self.apply_settings()
        
        # Setup UI
        self.setup_ui()
        
        # Initialize services
        self.ai_integration = AIIntegration()
        self.voice_manager = VoiceManager(self.handle_speech_input)
        
        # Start message processing
        asyncio.run_coroutine_threadsafe(self.process_message_queue(), self.loop)
        
        # Start status update loop
        threading.Thread(target=self._update_status_loop, daemon=True).start()
        
    def apply_settings(self):
        """Apply current settings to the application"""
        theme = self.settings_manager.get_setting("appearance", "theme")
        ctk.set_appearance_mode(theme)
        
        font_size = self.settings_manager.get_setting("appearance", "font_size")
        self.default_font = ("Helvetica", font_size)
        
    def show_settings(self):
        """Show settings dialog"""
        dialog = SettingsDialog(self, self.settings_manager, self.on_settings_changed)
        dialog.grab_set()
        
    def on_settings_changed(self):
        """Handle settings changes"""
        self.apply_settings()
        
        # Update UI elements
        self.history_display.configure(font=self.default_font)
        self.chat_display.configure(font=self.default_font)
        self.text_input.configure(font=self.default_font)
        
        # Update voice settings
        voice_settings = self.settings_manager.get_voice_settings()
        self.voice_manager.update_settings(voice_settings)
        
        # Update AI settings
        ai_settings = self.settings_manager.get_ai_settings()
        self.ai_integration.update_settings(ai_settings)
        
    def setup_ui(self):
        # Create main container with grid layout
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create sidebar for history
        self.sidebar = ctk.CTkFrame(self.container, width=200)
        self.sidebar.pack(side="left", fill="y", padx=(0, 10))
        
        # History label
        history_label = ctk.CTkLabel(
            self.sidebar,
            text="Command History",
            font=("Helvetica", 16, "bold")
        )
        history_label.pack(pady=(10, 5))
        
        # History display
        self.history_display = ctk.CTkTextbox(
            self.sidebar,
            width=180,
            height=400,
            font=("Helvetica", 12)
        )
        self.history_display.pack(pady=5, padx=10)
        
        # Chat area
        self.chat_area = ctk.CTkFrame(self.container)
        self.chat_area.pack(side="right", fill="both", expand=True)
        
        # Header Frame
        self.header_frame = ctk.CTkFrame(self.chat_area)
        self.header_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Title with custom styling
        title = ctk.CTkLabel(
            self.header_frame, 
            text="AI Assistant",
            font=("Helvetica", 28, "bold")
        )
        title.pack(side="left", pady=10)
        
        # Settings button
        self.settings_button = ctk.CTkButton(
            self.header_frame,
            text="⚙️ Settings",
            command=self.show_settings,
            width=100
        )
        self.settings_button.pack(side="right", padx=10)
        
        # Chat display area
        self.chat_frame = ctk.CTkFrame(self.chat_area)
        self.chat_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.chat_display = ctk.CTkTextbox(
            self.chat_frame,
            wrap="word",
            font=("Helvetica", 12),
            height=400
        )
        self.chat_display.pack(fill="both", expand=True, padx=5, pady=5)
        self.chat_display.configure(state="disabled")
        
        # Input area
        self.input_frame = ctk.CTkFrame(self.chat_area)
        self.input_frame.pack(fill="x", padx=10, pady=10)
        
        self.text_input = ctk.CTkTextbox(
            self.input_frame,
            height=60,
            font=("Helvetica", 12)
        )
        self.text_input.pack(side="left", fill="x", expand=True, padx=(5, 10))
        
        # Add voice control frame
        self.voice_frame = ctk.CTkFrame(self.input_frame)
        self.voice_frame.pack(side="right", padx=5)
        
        # Voice control button
        self.voice_button = ctk.CTkButton(
            self.voice_frame,
            text="🎤",
            width=40,
            command=self.toggle_voice_input
        )
        self.voice_button.pack(side="left")
        
        # Calibrate button
        self.calibrate_button = ctk.CTkButton(
            self.voice_frame,
            text="⚙️",
            width=40,
            command=self.calibrate_microphone
        )
        self.calibrate_button.pack(side="left", padx=5)
        
        # Button frame
        self.button_frame = ctk.CTkFrame(self.input_frame, fg_color="transparent")
        self.button_frame.pack(side="right", padx=5)
        
        # Send button
        self.send_button = ctk.CTkButton(
            self.button_frame,
            text="➤",
            width=60,
            height=60,
            command=self.handle_enter,
            font=("Helvetica", 20)
        )
        self.send_button.pack(side="left", padx=5)
        
        # Status bar
        self.status_frame = ctk.CTkFrame(self.chat_area)
        self.status_frame.pack(fill="x", padx=10, pady=(10, 0))
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Ready",
            font=("Helvetica", 12)
        )
        self.status_label.pack(side="left", padx=5)
        
        # Model selection
        self.model_var = ctk.StringVar(value="Both")
        self.model_menu = ctk.CTkOptionMenu(
            self.status_frame,
            values=["OpenAI", "Gemini", "Both"],
            variable=self.model_var
        )
        self.model_menu.pack(side="right", padx=5)
        
        # Bind enter key to send message
        self.text_input.bind("<Return>", self.handle_enter)
        self.text_input.bind("<Shift-Return>", self.handle_shift_enter)
        
    async def process_message_queue(self):
        """Process messages from the queue"""
        while True:
            try:
                message = await self.message_queue.get()
                if message:
                    await self.handle_message(message)
                await asyncio.sleep(0.1)  # Prevent CPU overuse
            except Exception as e:
                self.show_error(f"Error processing message: {str(e)}")
                
    async def handle_message(self, message: str):
        """Handle a single message"""
        try:
            self.is_processing = True
            self.update_status("Processing...", "yellow")
            
            # Add user message to chat
            self.append_message(message, "You")
            
            # Show typing indicator
            self.show_typing_indicator()
            
            try:
                # Get selected model
                model = self.model_var.get()
                
                # Get AI response
                response = await self.ai_integration.get_response(message, model)
                
                # Remove typing indicator and show response
                self.hide_typing_indicator()
                self.append_message(response, "Assistant")
                
            except Exception as e:
                self.hide_typing_indicator()
                self.show_error(f"AI Error: {str(e)}")
                
        except Exception as e:
            self.show_error(f"Error: {str(e)}")
        finally:
            self.is_processing = False
            self.update_status("Ready", "green")
            
    def show_typing_indicator(self):
        """Show typing indicator in chat"""
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", "\nAssistant is typing...\n")
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")
        
    def hide_typing_indicator(self):
        """Hide typing indicator from chat"""
        self.chat_display.configure(state="normal")
        self.chat_display.delete("end-2l", "end")
        self.chat_display.configure(state="disabled")
        
    def show_error(self, error_message: str):
        """Show error message in chat"""
        self.append_message(error_message, "System")
        
    def handle_enter(self, event=None):
        """Handle Enter key press"""
        if not event or not event.state & 0x1:  # No Shift key
            message = self.text_input.get("1.0", "end-1c").strip()
            if message:
                # Clear input
                self.text_input.delete("1.0", "end")
                # Add message to queue
                asyncio.run_coroutine_threadsafe(
                    self.message_queue.put(message),
                    self.loop
                )
            return "break"  # Prevent default newline
            
    def handle_shift_enter(self, event):
        """Handle Shift+Enter key press"""
        return None  # Allow default newline behavior
        
    def start_background_loop(self) -> None:
        """Start asyncio event loop in background"""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
        
    def run(self):
        try:
            self.mainloop()
        finally:
            # Cleanup
            self.loop.call_soon_threadsafe(self.loop.stop)
            self.thread.join(timeout=1)
            
    def cleanup(self):
        """Cleanup resources before closing"""
        if self.loop and self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)
            
        # Close any open resources
        self.ai_integration.cleanup()
        
    def __del__(self):
        self.cleanup()
        
    def update_status(self, message, color="white"):
        self.status_label.configure(text=message, text_color=color)
        
    def append_message(self, message, sender="You"):
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", f"\n{sender}: {message}\n")
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")
        
    def toggle_voice_input(self):
        """Toggle voice input on/off"""
        if self.voice_manager.is_listening:
            self.voice_manager.stop_listening()
            self.voice_button.configure(fg_color="gray")
            self.update_status("Voice input stopped", "gray")
        else:
            self.voice_manager.start_listening()
            self.voice_button.configure(fg_color="green")
            self.update_status("Listening...", "green")
            
    def calibrate_microphone(self):
        """Calibrate microphone for ambient noise"""
        self.update_status("Calibrating microphone...", "yellow")
        threading.Thread(target=self._do_calibration, daemon=True).start()
        
    def _do_calibration(self):
        """Run microphone calibration"""
        try:
            self.voice_manager.calibrate()
            self.update_status("Calibration complete", "green")
        except Exception as e:
            self.update_status(f"Calibration failed: {str(e)}", "red")
            
    def _update_status_loop(self):
        """Update status messages from voice manager"""
        while True:
            # Check for status updates
            status = self.voice_manager.get_status()
            if status:
                self.update_status(status, "blue")
                
            # Check for errors
            error = self.voice_manager.get_error()
            if error:
                self.update_status(error, "red")
                
            time.sleep(0.1)  # Prevent CPU overuse
            
    def handle_speech_input(self, text):
        """Handle recognized speech input"""
        self.text_input.delete("1.0", "end")
        self.text_input.insert("1.0", text)
        self.handle_enter()
        
if __name__ == "__main__":
    app = IntegratedAssistant()
    app.run()
