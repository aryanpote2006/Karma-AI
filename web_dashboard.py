"""
Web Dashboard Module for KARMA ULTRA PRO
Flask-based web interface for remote access and monitoring
"""

import os
import logging
import threading
from datetime import datetime
from pathlib import Path

# Flask imports
try:
    from flask import Flask, render_template_string, jsonify, request
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    logging.warning("Flask not available, web dashboard disabled")


class WebDashboard:
    """
    Web Dashboard for KARMA AI
    Features:
    - Command history viewer
    - Analytics dashboard
    - Remote control interface
    - Live status monitoring
    - Settings management
    """
    
    def __init__(self, karma_instance=None, port=5000, logger=None):
        """Initialize web dashboard"""
        self.logger = logger or logging.getLogger('KARMA-WebDashboard')
        self.port = port
        self.karma = karma_instance
        self.app = None
        self.server_thread = None
        self.running = False
        
        if FLASK_AVAILABLE:
            self._setup_flask()
        else:
            self.logger.warning("Web Dashboard requires Flask")
    
    def _setup_flask(self):
        """Setup Flask application"""
        self.app = Flask(__name__, template_folder=str(Path(__file__).parent / 'web' / 'templates'))
        self.app.static_folder = str(Path(__file__).parent / 'web' / 'static')
        
        # Routes
        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/api/status', 'api_status', self.api_status, methods=['GET'])
        self.app.add_url_rule('/api/commands', 'api_commands', self.api_commands, methods=['GET'])
        self.app.add_url_rule('/api/command', 'api_command', self.api_command, methods=['POST'])
        self.app.add_url_rule('/api/conversations', 'api_conversations', self.api_conversations, methods=['GET'])
        self.app.add_url_rule('/api/stats', 'api_stats', self.api_stats, methods=['GET'])
        self.app.add_url_rule('/api/execute', 'api_execute', self.api_execute, methods=['POST'])
        
        # HTML Templates
        self._setup_templates()
        
        self.logger.info(f"Web Dashboard configured on port {self.port}")
    
    def _setup_templates(self):
        """Setup HTML templates"""
        self.index_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KARMA AI - Ultra Pro</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        :root {
            --neon-blue: #00d4ff;
            --neon-cyan: #00fff7;
            --bg-dark: #0a0a12;
            --bg-medium: #12121f;
        }
        body {
            background: var(--bg-dark);
            color: white;
            font-family: 'Segoe UI', sans-serif;
        }
        .neon-text {
            color: var(--neon-blue);
            text-shadow: 0 0 10px var(--neon-blue);
        }
        .neon-border {
            border: 1px solid var(--neon-blue);
            box-shadow: 0 0 10px rgba(0, 212, 255, 0.3);
        }
        .card {
            background: var(--bg-medium);
            border-radius: 10px;
            padding: 20px;
            margin: 10px;
        }
        .btn {
            background: linear-gradient(135deg, #00d4ff, #007a99);
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
        }
        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 5px;
        }
        .online { background: #00ff88; }
        .offline { background: #ff4444; }
        .listening { background: #00d4ff; animation: pulse 1s infinite; }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
    </style>
</head>
<body>
    <div class="min-h-screen p-5">
        <!-- Header -->
        <header class="text-center mb-10">
            <h1 class="text-5xl font-bold neon-text">◈ KARMA ULTRA PRO</h1>
            <p class="text-gray-400 mt-2">Advanced AI Assistant Dashboard</p>
        </header>
        
        <!-- Status Bar -->
        <div class="card neon-border mb-5">
            <div class="flex justify-between items-center">
                <div>
                    <span class="status-dot online" id="statusDot"></span>
                    <span id="statusText" class="text-xl">Online</span>
                </div>
                <div class="text-gray-400">
                    <span id="currentTime"></span>
                </div>
            </div>
        </div>
        
        <!-- Main Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
            <!-- Quick Actions -->
            <div class="card">
                <h2 class="text-2xl font-bold mb-4 neon-text">Quick Actions</h2>
                <div class="grid grid-cols-2 gap-3">
                    <button onclick="sendCommand('listen')" class="btn">🎤 Listen</button>
                    <button onclick="sendCommand('status')" class="btn">📊 Status</button>
                    <button onclick="sendCommand('weather')" class="btn">🌤️ Weather</button>
                    <button onclick="sendCommand('time')" class="btn">⏰ Time</button>
                </div>
            </div>
            
            <!-- Statistics -->
            <div class="card">
                <h2 class="text-2xl font-bold mb-4 neon-text">Statistics</h2>
                <div id="stats" class="text-gray-300">
                    <p>Commands: <span id="cmdCount">-</span></p>
                    <p>Conversations: <span id="convCount">-</span></p>
                    <p>Uptime: <span id="uptime">-</span></p>
                </div>
            </div>
            
            <!-- Command Input -->
            <div class="card md:col-span-2">
                <h2 class="text-2xl font-bold mb-4 neon-text">Remote Control</h2>
                <div class="flex gap-3">
                    <input type="text" id="commandInput" placeholder="Enter command..." 
                           class="flex-1 bg-gray-800 border border-gray-700 rounded px-4 py-2 text-white">
                    <button onclick="executeCommand()" class="btn">Execute</button>
                </div>
                <div id="response" class="mt-4 p-3 bg-gray-800 rounded hidden"></div>
            </div>
            
            <!-- Recent Commands -->
            <div class="card md:col-span-2">
                <h2 class="text-2xl font-bold mb-4 neon-text">Recent Commands</h2>
                <div id="commandsList" class="max-h-60 overflow-y-auto">
                    <p class="text-gray-500">Loading...</p>
                </div>
            </div>
            
            <!-- Conversations -->
            <div class="card md:col-span-2">
                <h2 class="text-2xl font-bold mb-4 neon-text">Recent Conversations</h2>
                <div id="conversationsList" class="max-h-60 overflow-y-auto">
                    <p class="text-gray-500">Loading...</p>
                </div>
            </div>
        </div>
        
        <!-- Footer -->
        <footer class="text-center mt-10 text-gray-500">
            <p>KARMA AI v2.0 | Ultra Pro Edition</p>
        </footer>
    </div>
    
    <script>
        // Update time
        function updateTime() {
            document.getElementById('currentTime').textContent = new Date().toLocaleString();
        }
        setInterval(updateTime, 1000);
        updateTime();
        
        // Load status
        async function loadStatus() {
            try {
                const res = await fetch('/api/status');
                const data = await res.json();
                document.getElementById('cmdCount').textContent = data.stats?.commands || 0;
                document.getElementById('convCount').textContent = data.stats?.conversations || 0;
            } catch(e) { console.error(e); }
        }
        
        // Load commands
        async function loadCommands() {
            try {
                const res = await fetch('/api/commands');
                const commands = await res.json();
                const list = document.getElementById('commandsList');
                if (commands.length === 0) {
                    list.innerHTML = '<p class="text-gray-500">No commands yet</p>';
                } else {
                    list.innerHTML = commands.slice(0, 10).map(c => 
                        `<div class="p-2 border-b border-gray-700">
                            <span class="text-neon-blue">${c.command}</span>
                            <span class="text-gray-500 text-sm ml-2">${new Date(c.timestamp).toLocaleString()}</span>
                        </div>`
                    ).join('');
                }
            } catch(e) { console.error(e); }
        }
        
        // Load conversations
        async function loadConversations() {
            try {
                const res = await fetch('/api/conversations');
                const convs = await res.json();
                const list = document.getElementById('conversationsList');
                if (convs.length === 0) {
                    list.innerHTML = '<p class="text-gray-500">No conversations yet</p>';
                } else {
                    list.innerHTML = convs.slice(0, 10).map(c => 
                        `<div class="p-2 border-b border-gray-700">
                            <span class="text-neon-blue">You:</span> ${c.user_message}<br>
                            <span class="text-green-400">KARMA:</span> ${c.ai_message}
                        </div>`
                    ).join('');
                }
            } catch(e) { console.error(e); }
        }
        
        // Send command
        function sendCommand(cmd) {
            document.getElementById('commandInput').value = cmd;
            executeCommand();
        }
        
        // Execute command
        async function executeCommand() {
            const input = document.getElementById('commandInput');
            const cmd = input.value.trim();
            if (!cmd) return;
            
            const responseDiv = document.getElementById('response');
            responseDiv.classList.remove('hidden');
            responseDiv.textContent = 'Processing...';
            
            try {
                const res = await fetch('/api/execute', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({command: cmd})
                });
                const data = await res.json();
                responseDiv.textContent = data.response || data.error;
                loadCommands();
                loadConversations();
            } catch(e) {
                responseDiv.textContent = 'Error: ' + e.message;
            }
            
            input.value = '';
        }
        
        // Auto-refresh
        setInterval(() => {
            loadStatus();
            loadCommands();
            loadConversations();
        }, 5000);
        
        loadStatus();
        loadCommands();
        loadConversations();
    </script>
</body>
</html>
'''
    
    def index(self):
        """Main dashboard page"""
        return render_template_string(self.index_template)
    
    def api_status(self):
        """API: Get system status"""
        stats = {}
        if self.karma and hasattr(self.karma, 'memory'):
            try:
                stats = self.karma.memory.get_stats()
            except:
                pass
        
        return jsonify({
            'status': 'online',
            'timestamp': datetime.now().isoformat(),
            'stats': stats
        })
    
    def api_commands(self):
        """API: Get command history"""
        commands = []
        if self.karma and hasattr(self.karma, 'memory'):
            try:
                history = self.karma.memory.get_conversation_history(50)
                commands = [{'command': h.get('content', ''), 'timestamp': h.get('timestamp', '')} 
                           for h in history if h.get('role') == 'user']
            except:
                pass
        
        return jsonify(commands)
    
    def api_command(self):
        """API: Send command"""
        data = request.get_json()
        command = data.get('command', '')
        
        response = 'Command processed'
        if self.karma and hasattr(self.karma, 'command_processor'):
            try:
                response = self.karma.command_processor.process(command) or 'No response'
            except Exception as e:
                response = f'Error: {str(e)}'
        
        return jsonify({'response': response})
    
    def api_conversations(self):
        """API: Get conversations"""
        conversations = []
        if self.karma and hasattr(self.karma, 'memory'):
            try:
                history = self.karma.memory.get_conversation_history(20)
                conversations = history
            except:
                pass
        
        return jsonify(conversations)
    
    def api_stats(self):
        """API: Get statistics"""
        stats = {}
        if self.karma and hasattr(self.karma, 'memory'):
            try:
                stats = self.karma.memory.get_stats()
            except:
                pass
        
        return jsonify(stats)
    
    def api_execute(self):
        """API: Execute command remotely"""
        data = request.get_json()
        command = data.get('command', '')
        
        if not command:
            return jsonify({'error': 'No command provided'}), 400
        
        response_text = 'Processing...'
        success = True
        
        if self.karma:
            try:
                # Process command
                if hasattr(self.karma, 'command_processor'):
                    response_text = self.karma.command_processor.process(command) or 'No response'
                
                # Speak response if voice engine available
                if hasattr(self.karma, 'voice_engine'):
                    self.karma.voice_engine.speak_async(response_text)
                    
            except Exception as e:
                response_text = f'Error: {str(e)}'
                success = False
        
        return jsonify({
            'response': response_text,
            'success': success,
            'command': command
        })
    
    def start(self):
        """Start web dashboard in background thread"""
        if not FLASK_AVAILABLE:
            self.logger.error("Flask not available")
            return
        
        if self.running:
            self.logger.warning("Web dashboard already running")
            return
        
        def run_server():
            self.app.run(host='0.0.0.0', port=self.port, debug=False, use_reloader=False)
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        self.running = True
        
        self.logger.info(f"Web Dashboard started at http://localhost:{self.port}")
    
    def stop(self):
        """Stop web dashboard"""
        self.running = False
        # Note: Flask doesn't have clean shutdown, thread will die on process exit


# Singleton
_dashboard = None

def get_web_dashboard(karma_instance=None, port=5000, logger=None):
    """Get or create web dashboard singleton"""
    global _dashboard
    if _dashboard is None:
        _dashboard = WebDashboard(karma_instance, port, logger)
    return _dashboard
