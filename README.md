# Integrated AI Assistant 2.0

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

## Building the Application

To create an executable:

1. Ensure all dependencies are installed:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-exe.txt
   ```

2. Run the build script:
   ```bash
   python build_exe.py
   ```

The executable will be created in the `dist` directory. Note: Build artifacts are not included in the repository due to size limitations.

## Development

- Source code is in the `src` directory
- Tests are in the `tests` directory
- Run tests with: `pytest tests/`

## Project Structure
```
/IntegratedAssistant
├── src/
│   ├── assistant_core/    # Core assistant functionality
│   ├── main.py           # Entry point
│   └── test_*.py         # Test files
├── tests/                # Test directory
├── data/                 # Data storage
├── requirements.txt      # Python dependencies
├── requirements-exe.txt  # Build dependencies
└── build_exe.py         # Build script
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
