"""
KARMA AI Web Interface
Flask-based modern web interface for KARMA AI
Connects to existing voice engine and command processor
"""

import os
import sys
import logging
import threading
import json
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from voice_engine import VoiceEngine
from command_processor import CommandProcessor
from ai_brain import AIBrain
from memory import Memory
from automation import Automation
from musicLibrary import MusicLibrary

# Flask app setup
app = Flask(__name__,
            template_folder='templates',
            static_folder='static')
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('KARMA-Web')

# Global state
karma_instance = None
voice_engine = None
command_processor = None


def init_karma_components():
    """Initialize KARMA AI components"""
    global karma_instance, voice_engine, command_processor
    
    logger.info("Initializing KARMA AI components...")
    
    # Initialize components
    memory = Memory()
    ai_brain = AIBrain(memory)
    automation = Automation(logger)
    music_library = MusicLibrary()
    voice_engine = VoiceEngine(logger)
    command_processor = CommandProcessor(
        ai_brain,
        automation,
        music_library,
        memory,
        logger
    )
    
    logger.info("KARMA AI components initialized")
    return voice_engine, command_processor


# Initialize on startup
voice_engine, command_processor = init_karma_components()


@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')


@app.route('/api/status')
def get_status():
    """Get current KARMA AI status"""
    return jsonify({
        'status': 'online',
        'is_listening': voice_engine.is_listening if voice_engine else False,
        'is_speaking': voice_engine.is_speaking if voice_engine else False,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/command', methods=['POST'])
def process_command():
    """Process a voice/text command"""
    try:
        data = request.get_json()
        command = data.get('command', '').strip()
        
        if not command:
            return jsonify({'success': False, 'error': 'Empty command'}), 400
        
        logger.info(f"Processing command: {command}")
        
        # Process command in background thread
        result = {'success': False, 'response': '', 'error': None}
        
        def process():
            try:
                response = command_processor.process(command)
                result['success'] = True
                result['response'] = response
                
                # Speak the response
                if voice_engine and response:
                    voice_engine.speak_async(response)
            except Exception as e:
                logger.error(f"Command processing error: {e}")
                result['error'] = str(e)
        
        thread = threading.Thread(target=process, daemon=True)
        thread.start()
        thread.join(timeout=30)  # Wait for processing
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"API error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/voice/start', methods=['POST'])
def start_voice():
    """Start voice recognition"""
    try:
        if not voice_engine:
            return jsonify({'success': False, 'error': 'Voice engine not initialized'}), 500
        
        # Start listening in background
        def listen_loop():
            try:
                command = voice_engine.listen_for_command(timeout=10, phrase_time_limit=10)
                if command:
                    logger.info(f"Voice command: {command}")
                    # Process command
                    response = command_processor.process(command)
                    if response:
                        voice_engine.speak_async(response)
            except Exception as e:
                logger.error(f"Voice listening error: {e}")
        
        thread = threading.Thread(target=listen_loop, daemon=True)
        thread.start()
        
        return jsonify({'success': True, 'message': 'Listening started'})
        
    except Exception as e:
        logger.error(f"Voice start error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/voice/stop', methods=['POST'])
def stop_voice():
    """Stop voice recognition"""
    try:
        if voice_engine:
            voice_engine.stop()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/speak', methods=['POST'])
def speak_text():
    """Make KARMA speak text"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if text and voice_engine:
            voice_engine.speak_async(text)
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'No text provided'}), 400
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/history')
def get_history():
    """Get command history"""
    try:
        if command_processor and hasattr(command_processor, 'memory'):
            history = command_processor.memory.get_conversation()
            return jsonify({'success': True, 'history': history})
        return jsonify({'success': True, 'history': []})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/tasks')
def get_tasks():
    """Get task list"""
    try:
        if command_processor and hasattr(command_processor, 'memory'):
            tasks = command_processor.memory.get_tasks()
            return jsonify({'success': True, 'tasks': tasks})
        return jsonify({'success': True, 'tasks': []})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    print("=" * 50)
    print("🚀 KARMA AI Web Interface")
    print("=" * 50)
    print("Starting web server at http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
