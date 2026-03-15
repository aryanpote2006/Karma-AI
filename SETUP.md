# KARMA AI - Setup Instructions

## Overview
KARMA AI is an advanced AI personal assistant inspired by JARVIS from Iron Man. It features voice recognition, AI-powered conversations, system automation, and a beautiful JARVIS-style GUI dashboard.

## What's New in v2.0
- ✨ **Enhanced JARVIS GUI** - CustomTkinter-based neon blue interface
- 🎭 **Face Recognition Login** - Security with OpenCV
- 🌤️ **Weather & AQI** - Real-time weather and air quality data
- 📊 **System Monitor** - CPU, RAM, Battery status in GUI
- 🎤 **Improved Voice** - Better wake word detection

## Prerequisites

### System Requirements
- Windows 10/11 or macOS/Linux
- Python 3.8 or higher
- Microphone for voice input
- Speakers for voice output
- Webcam (for face recognition - optional)

### Required Software
1. Python 3.8+ (Download from python.org)
2. pip (comes with Python)

## Installation Steps

### Step 1: Install Python
1. Download Python from https://www.python.org/downloads/
2. Run the installer
3. **Important**: Check "Add Python to PATH"
4. Verify installation:
```
python --version
```

### Step 2: Install Dependencies
Navigate to the karma_ai folder and install requirements:

```
cd karma_ai
pip install -r requirements.txt
```

### Step 3: Install Audio Drivers (Windows)
For Windows, you may need to install PyAudio:

```
# If you get errors, try:
pip install pipwin
pipwin install pyaudio
```

For macOS:
```
brew install portaudio
pip install pyaudio
```

For Linux:
```
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio
```

## API Configuration (Optional)

### Google Gemini API (default AI - already configured)
The assistant comes pre-configured with a demo Gemini API key. For production:
1. Get an API key from https://aistudio.google.com/app/apikey
2. Edit ai_brain.py and replace the API key

### OpenAI API (alternative AI)
1. Get an API key from https://platform.openai.com/api-keys
2. Set the environment variable:
```
# Windows
setx OPENAI_API_KEY "your-api-key-here"

# Linux/Mac
export OPENAI_API_KEY="your-api-key-here"
```

## Running KARMA AI

### Option 1: With Enhanced GUI (Recommended)
```
python main.py
```

### Option 2: Voice Only Mode
```
python main.py --voice-only
```

### Option 3: No GUI
```
python main.py --no-gui
```

## Voice Commands

### Wake Word
- Say "Hey Karma" to activate voice mode

### Basic Commands
- "Open Google/YouTube/Facebook/LinkedIn"
- "Play [song name]"
- "What's the time/date?"
- "Weather" / "Air quality" / "AQI"
- "News"

### System Controls
- "Shutdown" / "Restart"
- "Volume up/down" / "Set volume 50"
- "Take a screenshot"
- "Lock screen"

### Task Management
- "Add task [task name]"
- "Show my tasks"
- "Set alarm 7 AM"

### AI Conversations
- Ask questions naturally
- Have conversations
- Get help with tasks

## Project Structure

```
karma_ai/
├── main.py              # Main entry point
├── voice_engine.py      # Voice recognition & TTS
├── command_processor.py # Command routing
├── automation.py        # System automation
├── ai_brain.py         # AI conversation (Gemini)
├── memory.py           # Data & history storage
├── gui.py              # Standard GUI dashboard
├── gui_enhanced.py     # JARVIS-style Enhanced GUI
├── vision.py           # Face Recognition
├── weather.py          # Weather & AQI
├── musicLibrary.py     # Music library
├── requirements.txt    # Python dependencies
├── data/               # User data storage
└── logs/               # Log files
```

## Troubleshooting

### Microphone Not Detected
1. Check microphone is connected
2. Grant microphone permissions to Python
3. Run: `python -c "import speech_recognition; print(speech_recognition.Microphone().list_microphone_names())"`

### Audio Output Issues
1. Check speakers are working
2. Try a different TTS voice
3. Run: `python -c "import pyttsx3; engine = pyttsx3.init(); engine.say('test'); engine.runAndWait()"`

### Face Recognition Not Working
1. Ensure webcam is connected
2. Install opencv-python: `pip install opencv-python`
3. Check logs for errors

### GUI Not Loading
1. Install CustomTkinter: `pip install customtkinter`
2. Try running with --no-gui flag to test voice functionality

### Import Errors
1. Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`
2. Make sure you're in the correct directory

## Customization

### Change Wake Word
Edit memory.py and change:
```
python
'wake_word': 'hey karma',
```

### Add Custom Songs
Edit musicLibrary.py and add to the self.music dictionary:
```
python
'my song': 'https://www.youtube.com/watch?v=...',
```

### Add Custom Applications
Edit automation.py and add to app_paths:
```
python
'app_name': 'C:\\path\\to\\app.exe',
```

### Enable Face Login
1. Run the assistant
2. Use vision.enroll_face() to add users
3. Set require_face_login=True in main.py

## Features

### Voice & AI
✓ Natural human-like voice response (pyttsx3)
✓ Faster listening response
✓ Continuous background listening
✓ Smart wake word detection ("Hey Karma")
✓ AI conversations with Gemini API

### AI Brain
✓ Google Gemini API integration
✓ Context memory
✓ Conversational chatbot
✓ Question answering
✓ Fallback to rule-based responses

### Automation
✓ Open applications (Chrome, VS Code, Notepad, etc.)
✓ System control (shutdown, restart, volume, brightness)
✓ Screenshot capture
✓ File searching
✓ Internet search
✓ WhatsApp messaging

### Smart Tasks
✓ To-do list management
✓ Alarms & reminders
✓ Schedule management

### Enhanced GUI (JARVIS Style)
✓ CustomTkinter dark theme
✓ Neon blue color scheme
✓ Animated status indicators
✓ System monitoring (CPU, RAM, Battery)
✓ Digital clock with date
✓ Voice command input
✓ Conversation history

### Security (v2.0)
✓ Face recognition login (OpenCV)
✓ Authorized user management
✓ Photo capture

### Weather & Environment (v2.0)
✓ Current weather conditions
✓ Air Quality Index (AQI)
✓ Weather descriptions for TTS

## Support

For issues and questions:
1. Check the logs in logs/ folder
2. Verify all dependencies are installed
3. Ensure microphone/speakers are working
4. Check API keys are configured (for AI features)

## License

This project is for educational purposes. Use responsibly.

## Credits
- Inspired by JARVIS from Iron Man
- Voice: pyttsx3
- AI: Google Gemini / OpenAI
- GUI: CustomTkinter
- Face Recognition: OpenCV
