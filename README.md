# Integrated AI Assistant

A powerful AI assistant that combines voice recognition, system control, and a modern GUI interface.

## Features
- Voice Recognition for hands-free control
- System automation and control
- Modern GUI interface
- AI-powered responses and actions

## Setup Instructions

1. Install Python 3.8 or higher if not already installed
2. Install required system dependencies:
   - For PyAudio (Windows):
     ```
     pip install pipwin
     pipwin install pyaudio
     ```
   - For other platforms, you might need portaudio:
     ```
     # Ubuntu/Debian
     sudo apt-get install python3-pyaudio
     # macOS
     brew install portaudio
     ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Unix/macOS
   source venv/bin/activate
   ```

4. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Set up environment variables:
   - Create a `.env` file in the project root
   - Add your OpenAI API key:
     ```
     OPENAI_API_KEY=your_api_key_here
     ```

## Project Structure
```
/IntegratedAssistant
├── /src
│   ├── voice_module/          # Voice recognition components
│   ├── system_control/        # System automation
│   ├── gui/                   # User interface
│   ├── assistant_core/        # AI logic
│   └── main.py               # Main application
├── requirements.txt
└── README.md
```

## Usage
1. Activate the virtual environment
2. Run the main application:
   ```bash
   python src/main.py
   ```

## Features
1. Voice Commands:
   - "Open [program]"
   - "Search for [query]"
   - "Control system [action]"

2. System Control:
   - Process management
   - Application control
   - System monitoring

3. GUI Features:
   - Modern dark/light theme
   - Real-time system monitoring
   - Command history
   - Settings configuration
