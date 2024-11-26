import speech_recognition as sr
import threading
import time
from typing import Callable, Dict, Any

class VoiceManager:
    def __init__(self, callback: Callable[[str], None]):
        self.callback = callback
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_listening = False
        self.thread = None
        
        # Default settings
        self.settings = {
            "language": "en-US",
            "energy_threshold": 4000,
            "pause_threshold": 0.8,
            "dynamic_energy": True,
            "auto_calibrate": True
        }
        
        # Apply initial settings
        self.apply_settings()
        
    def apply_settings(self):
        """Apply current settings to the recognizer"""
        self.recognizer.energy_threshold = self.settings["energy_threshold"]
        self.recognizer.pause_threshold = self.settings["pause_threshold"]
        self.recognizer.dynamic_energy_threshold = self.settings["dynamic_energy"]
        
        if self.settings["auto_calibrate"]:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
                
    def update_settings(self, new_settings: Dict[str, Any]):
        """Update voice recognition settings"""
        self.settings.update(new_settings)
        self.apply_settings()
        
    def start_listening(self):
        """Start listening for voice input"""
        if not self.is_listening:
            self.is_listening = True
            self.thread = threading.Thread(target=self._listen_loop)
            self.thread.daemon = True
            self.thread.start()
            
    def stop_listening(self):
        """Stop listening for voice input"""
        self.is_listening = False
        if self.thread:
            self.thread.join()
            
    def _listen_loop(self):
        """Main listening loop"""
        while self.is_listening:
            try:
                with self.microphone as source:
                    audio = self.recognizer.listen(source)
                    
                try:
                    text = self.recognizer.recognize_google(
                        audio,
                        language=self.settings["language"]
                    )
                    if text:
                        self.callback(text)
                except sr.UnknownValueError:
                    print("Could not understand audio")
                except sr.RequestError as e:
                    print(f"Could not request results; {e}")
                    
            except Exception as e:
                print(f"Error in voice recognition: {e}")
                time.sleep(1)  # Prevent rapid retries on error
                
    def calibrate_microphone(self):
        """Calibrate microphone for ambient noise"""
        try:
            with self.microphone as source:
                print("Calibrating microphone...")
                self.recognizer.adjust_for_ambient_noise(source)
                print("Calibration complete")
        except Exception as e:
            print(f"Error calibrating microphone: {e}")
            
    def __del__(self):
        """Cleanup when object is destroyed"""
        self.stop_listening()
