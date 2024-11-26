import os
import subprocess
import sys

def build_executable():
    print("Building AI Assistant Executable...")
    
    # Install requirements
    print("Installing requirements...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements-exe.txt"])
    
    # Build executable
    print("Creating executable...")
    subprocess.run([
        "pyinstaller",
        "--name=AI_Assistant",
        "--onefile",
        "--windowed",
        "--add-data=.env;.",
        "launcher.py"
    ])
    
    print("\nBuild complete! The executable can be found in the 'dist' folder.")

if __name__ == "__main__":
    build_executable()
