import customtkinter as ctk
from typing import Callable
from .settings_manager import SettingsManager

class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, parent, settings_manager: SettingsManager, on_close: Callable = None):
        super().__init__(parent)
        
        self.settings_manager = settings_manager
        self.on_close = on_close
        
        # Window setup
        self.title("Settings")
        self.geometry("600x500")
        
        # Create tabs
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add tabs
        self.tab_appearance = self.tabview.add("Appearance")
        self.tab_ai = self.tabview.add("AI")
        self.tab_voice = self.tabview.add("Voice")
        self.tab_system = self.tabview.add("System")
        self.tab_notifications = self.tabview.add("Notifications")
        
        # Setup each tab
        self.setup_appearance_tab()
        self.setup_ai_tab()
        self.setup_voice_tab()
        self.setup_system_tab()
        self.setup_notifications_tab()
        
        # Add buttons
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(fill="x", padx=10, pady=10)
        
        self.save_button = ctk.CTkButton(
            self.button_frame,
            text="Save",
            command=self.save_settings
        )
        self.save_button.pack(side="right", padx=5)
        
        self.cancel_button = ctk.CTkButton(
            self.button_frame,
            text="Cancel",
            command=self.cancel
        )
        self.cancel_button.pack(side="right", padx=5)
        
        self.reset_button = ctk.CTkButton(
            self.button_frame,
            text="Reset All",
            command=self.reset_all
        )
        self.reset_button.pack(side="left", padx=5)
        
    def setup_appearance_tab(self):
        """Setup appearance settings"""
        frame = ctk.CTkFrame(self.tab_appearance)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Theme selection
        theme_label = ctk.CTkLabel(frame, text="Theme:")
        theme_label.pack(anchor="w", padx=10, pady=5)
        
        self.theme_var = ctk.StringVar(value=self.settings_manager.get_setting("appearance", "theme"))
        theme_menu = ctk.CTkOptionMenu(
            frame,
            values=["dark", "light"],
            variable=self.theme_var
        )
        theme_menu.pack(anchor="w", padx=10, pady=5)
        
        # Font size
        size_label = ctk.CTkLabel(frame, text="Font Size:")
        size_label.pack(anchor="w", padx=10, pady=5)
        
        self.size_var = ctk.IntVar(value=self.settings_manager.get_setting("appearance", "font_size"))
        size_slider = ctk.CTkSlider(
            frame,
            from_=8,
            to=20,
            variable=self.size_var
        )
        size_slider.pack(anchor="w", padx=10, pady=5, fill="x")
        
    def setup_ai_tab(self):
        """Setup AI settings"""
        frame = ctk.CTkFrame(self.tab_ai)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Default model
        model_label = ctk.CTkLabel(frame, text="Default Model:")
        model_label.pack(anchor="w", padx=10, pady=5)
        
        self.model_var = ctk.StringVar(value=self.settings_manager.get_setting("ai", "default_model"))
        model_menu = ctk.CTkOptionMenu(
            frame,
            values=["OpenAI", "Gemini", "Both"],
            variable=self.model_var
        )
        model_menu.pack(anchor="w", padx=10, pady=5)
        
        # Temperature
        temp_label = ctk.CTkLabel(frame, text="Temperature:")
        temp_label.pack(anchor="w", padx=10, pady=5)
        
        self.temp_var = ctk.DoubleVar(value=self.settings_manager.get_setting("ai", "temperature"))
        temp_slider = ctk.CTkSlider(
            frame,
            from_=0,
            to=1,
            variable=self.temp_var
        )
        temp_slider.pack(anchor="w", padx=10, pady=5, fill="x")
        
    def setup_voice_tab(self):
        """Setup voice settings"""
        frame = ctk.CTkFrame(self.tab_voice)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Language selection
        lang_label = ctk.CTkLabel(frame, text="Language:")
        lang_label.pack(anchor="w", padx=10, pady=5)
        
        self.lang_var = ctk.StringVar(value=self.settings_manager.get_setting("voice", "language"))
        lang_menu = ctk.CTkOptionMenu(
            frame,
            values=["en-US", "es-ES", "fr-FR", "de-DE"],
            variable=self.lang_var
        )
        lang_menu.pack(anchor="w", padx=10, pady=5)
        
        # Auto calibration
        self.auto_cal_var = ctk.BooleanVar(value=self.settings_manager.get_setting("voice", "auto_calibrate"))
        auto_cal_check = ctk.CTkCheckBox(
            frame,
            text="Auto Calibrate",
            variable=self.auto_cal_var
        )
        auto_cal_check.pack(anchor="w", padx=10, pady=5)
        
    def setup_system_tab(self):
        """Setup system settings"""
        frame = ctk.CTkFrame(self.tab_system)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Auto save
        self.auto_save_var = ctk.BooleanVar(value=self.settings_manager.get_setting("system", "auto_save"))
        auto_save_check = ctk.CTkCheckBox(
            frame,
            text="Auto Save",
            variable=self.auto_save_var
        )
        auto_save_check.pack(anchor="w", padx=10, pady=5)
        
        # History size
        hist_label = ctk.CTkLabel(frame, text="Command History Size:")
        hist_label.pack(anchor="w", padx=10, pady=5)
        
        self.hist_var = ctk.IntVar(value=self.settings_manager.get_setting("system", "command_history_size"))
        hist_slider = ctk.CTkSlider(
            frame,
            from_=10,
            to=500,
            variable=self.hist_var
        )
        hist_slider.pack(anchor="w", padx=10, pady=5, fill="x")
        
    def setup_notifications_tab(self):
        """Setup notification settings"""
        frame = ctk.CTkFrame(self.tab_notifications)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Sound notifications
        self.sound_var = ctk.BooleanVar(value=self.settings_manager.get_setting("notifications", "sound_enabled"))
        sound_check = ctk.CTkCheckBox(
            frame,
            text="Sound Notifications",
            variable=self.sound_var
        )
        sound_check.pack(anchor="w", padx=10, pady=5)
        
        # Visual notifications
        self.visual_var = ctk.BooleanVar(value=self.settings_manager.get_setting("notifications", "visual_enabled"))
        visual_check = ctk.CTkCheckBox(
            frame,
            text="Visual Notifications",
            variable=self.visual_var
        )
        visual_check.pack(anchor="w", padx=10, pady=5)
        
    def save_settings(self):
        """Save all settings"""
        # Appearance
        self.settings_manager.update_setting("appearance", "theme", self.theme_var.get())
        self.settings_manager.update_setting("appearance", "font_size", self.size_var.get())
        
        # AI
        self.settings_manager.update_setting("ai", "default_model", self.model_var.get())
        self.settings_manager.update_setting("ai", "temperature", self.temp_var.get())
        
        # Voice
        self.settings_manager.update_setting("voice", "language", self.lang_var.get())
        self.settings_manager.update_setting("voice", "auto_calibrate", self.auto_cal_var.get())
        
        # System
        self.settings_manager.update_setting("system", "auto_save", self.auto_save_var.get())
        self.settings_manager.update_setting("system", "command_history_size", self.hist_var.get())
        
        # Notifications
        self.settings_manager.update_setting("notifications", "sound_enabled", self.sound_var.get())
        self.settings_manager.update_setting("notifications", "visual_enabled", self.visual_var.get())
        
        if self.on_close:
            self.on_close()
        self.destroy()
        
    def cancel(self):
        """Cancel settings changes"""
        if self.on_close:
            self.on_close()
        self.destroy()
        
    def reset_all(self):
        """Reset all settings to defaults"""
        self.settings_manager.reset_all()
        if self.on_close:
            self.on_close()
        self.destroy()
