import subprocess
import sys
import os
import platform

def install_dependencies():
    print("🚀 Setting up Integrated AI Assistant...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required. Please upgrade.")
        sys.exit(1)
    
    # Determine pip command
    pip_command = sys.executable + " -m pip"
    
    # Upgrade pip
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    
    # Install requirements
    try:
        subprocess.check_call([pip_command, "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
    except subprocess.CalledProcessError:
        print("❌ Error installing dependencies. Please check your internet connection.")
        sys.exit(1)
    
    # Additional setup
    try:
        # NLTK data download
        import nltk
        nltk.download('punkt', quiet=True)
        nltk.download('wordnet', quiet=True)
        
        print("🧠 Additional language resources downloaded.")
    except Exception as e:
        print(f"⚠️ Warning: Could not download additional resources: {e}")
    
    # Environment setup
    print("\n🔧 Setup Complete!")
    print("Next steps:")
    print("1. Set your OpenAI/Gemini API keys in .env")
    print("2. Run the assistant with: python launcher.py")

def main():
    install_dependencies()

if __name__ == "__main__":
    main()
