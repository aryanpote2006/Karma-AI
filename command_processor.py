"""
Command Processor Module for KARMA AI
Processes user commands and routes them to appropriate handlers
"""

import re
import logging
import webbrowser
from datetime import datetime, timedelta


class CommandProcessor:
    """
    Processes and executes user commands
    Routes commands to appropriate modules (AI, Automation, Music, Weather, etc.)
    """
    
    def __init__(self, ai_brain, automation, music_library, memory, logger=None, weather=None):
        """Initialize command processor with dependencies"""
        self.logger = logger or logging.getLogger('KARMA-Commands')
        self.ai_brain = ai_brain
        self.automation = automation
        self.music_library = music_library
        self.memory = memory
        self.weather = weather
        
        # Command patterns
        self._setup_command_patterns()
        
        # Memory storage
        self.user_memories = {}
        
        self.logger.info("Command Processor initialized")
    
    def _setup_command_patterns(self):
        """Setup regex patterns for command matching"""
        # Website commands
        self.website_patterns = {
            r'open\s+(?:google|search)': 'https://www.google.com',
            r'open\s+youtube': 'https://www.youtube.com',
            r'open\s+facebook': 'https://www.facebook.com',
            r'open\s+linkedin': 'https://www.linkedin.com',
            r'open\s+twitter': 'https://twitter.com',
            r'open\s+instagram': 'https://instagram.com',
            r'open\s+github': 'https://github.com',
            r'open\s+reddit': 'https://www.reddit.com',
            r'open\s+gmail': 'https://mail.google.com',
            r'open\s+whatsapp': 'https://web.whatsapp.com',
            r'open\s+netflix': 'https://www.netflix.com',
            r'open\s+amazon': 'https://www.amazon.com',
        }
        
        # System commands
        self.system_patterns = {
            r'shutdown': 'shutdown',
            r'restart|reboot': 'restart',
            r'sleep': 'sleep',
            r'lock': 'lock',
        }
        
        # Music commands
        self.music_patterns = {
            r'play\s+(.+)': 'play',
            r'pause': 'pause',
            r'stop\s+music': 'stop',
            r'next\s+song': 'next',
            r'previous\s+song': 'previous',
        }
        
        # Volume commands
        self.volume_patterns = {
            r'volume\s+up': ('volume', 'up'),
            r'volume\s+down': ('volume', 'down'),
            r'set\s+volume\s+(\d+)': ('volume', 'set'),
            r'mute': ('volume', 'mute'),
        }
        
        # App commands
        self.app_patterns = {
            r'open\s+chrome': 'chrome',
            r'open\s+(?:vs\s*code|visual\s*studio)': 'vscode',
            r'open\s+notepad': 'notepad',
            r'open\s+word': 'word',
            r'open\s+excel': 'excel',
            r'open\s+powerpoint': 'powerpoint',
            r'open\s+calculator': 'calculator',
            r'open\s+settings': 'settings',
        }
        
        # Info commands
        self.info_patterns = {
            r'what\s+is\s+the\s+time': 'time',
            r'what\s+time\s+is\s+it': 'time',
            r'what\s+is\s+the\s+date': 'date',
            r'what\s+day\s+is\s+it': 'day',
            r'weather': 'weather',
            r'what\s+is\s+the\s+weather': 'weather',
            r'how\s+is\s+the\s+weather': 'weather',
            r'air\s+quality': 'aqi',
            r'aqi': 'aqi',
            r'pollution': 'aqi',
            r'news': 'news',
        }
        
        # Task commands
        self.task_patterns = {
            r'add\s+(?:to\s+)?(?:my\s+)?(todo|to-do|list)': 'add_task',
            r'show\s+(?:my\s+)?(todo|to-do|list)': 'show_tasks',
            r'remove\s+task\s+(\d+)': 'remove_task',
            r'complete\s+task\s+(\d+)': 'complete_task',
            r'set\s+(?:an\s+)?alarm\s+(.+)': 'set_alarm',
            r'set\s+reminder\s+(.+)': 'set_reminder',
            r'create\s+(?:a\s+)?schedule': 'create_schedule',
        }
        
        # Memory commands (NEW)
        self.memory_patterns = {
            r'remember\s+that\s+(.+)': 'remember',
            r'remember\s+(.+)': 'remember',
            r'what\s+do\s+you\s+remember': 'what_remember',
            r'what\s+do\s+you\s+know\s+about\s+me': 'what_remember',
            r'forget\s+everything': 'forget',
        }
        
        # YouTube commands
        self.youtube_patterns = {
            r'play\s+(?:on\s+)?youtube\s+(.+)': 'play_youtube',
            r'play\s+(.+)\s+on\s+youtube': 'play_youtube',
            r'search\s+(?:on\s+)?youtube\s+(.+)': 'search_youtube',
            r'youtube\s+search\s+(.+)': 'search_youtube',
            r'play\s+youtube': 'open_youtube',
            r'pause\s+(?:youtube\s+)?video': 'youtube_pause',
            r'resume\s+(?:youtube\s+)?video': 'youtube_play',
            r'youtube\s+next': 'youtube_next',
        }
        
        # YouTube controller (lazy import)
        self.youtube_controller = None
    
    def process(self, command):
        """
        Process a user command
        
        Args:
            command: Raw command string from user
            
        Returns:
            Response string to speak back to user
        """
        if not command:
            return None
        
        command = command.lower().strip()
        self.logger.info(f"Processing command: {command}")
        
        # Save to memory
        self.memory.add_to_history('user', command)
        
        # Check for AI conversation (default fallback)
        # Process commands in priority order
        
        # 1. Website commands
        response = self._handle_website(command)
        if response:
            return response
        
        # 2. System commands
        response = self._handle_system(command)
        if response:
            return response
        
        # 3. Music commands
        response = self._handle_music(command)
        if response:
            return response
        
        # 4. Volume commands
        response = self._handle_volume(command)
        if response:
            return response
        
        # 5. App commands
        response = self._handle_apps(command)
        if response:
            return response
        
        # 6. Info commands
        response = self._handle_info(command)
        if response:
            return response
        
        # 7. Task commands
        response = self._handle_tasks(command)
        if response:
            return response
        
        # 8. WhatsApp commands
        response = self._handle_whatsapp(command)
        if response:
            return response
        
        # 9. Search commands
        response = self._handle_search(command)
        if response:
            return response
        
        # 10. Memory commands
        response = self._handle_memory(command)
        if response:
            return response
        
        # 11. YouTube commands
        response = self._handle_youtube(command)
        if response:
            return response
        
        # 12. Fallback to AI brain for conversation
        return self._handle_ai_conversation(command)
    
    def _handle_youtube(self, command):
        """Handle YouTube commands"""
        # Lazy import YouTube controller
        if self.youtube_controller is None:
            try:
                from youtube import YouTubeController
                self.youtube_controller = YouTubeController(self.logger)
            except Exception as e:
                self.logger.error(f"YouTube controller error: {e}")
                return None
        
        for pattern, action in self.youtube_patterns.items():
            match = re.search(pattern, command)
            if match:
                if action == 'play_youtube' and match.groups():
                    query = match.group(1)
                    return self.youtube_controller.play_video(query)
                elif action == 'search_youtube' and match.groups():
                    query = match.group(1)
                    return self.youtube_controller.search(query)
                elif action == 'open_youtube':
                    import webbrowser
                    webbrowser.open('https://www.youtube.com')
                    return "Opening YouTube"
                elif action == 'youtube_pause':
                    return self.youtube_controller.control_playback('pause')
                elif action == 'youtube_play':
                    return self.youtube_controller.control_playback('play')
                elif action == 'youtube_next':
                    return self.youtube_controller.control_playback('next')
        
        return None
    
    def _handle_website(self, command):
        """Handle website opening commands"""
        # First check predefined websites
        for pattern, url in self.website_patterns.items():
            if re.search(pattern, command):
                webbrowser.open(url)
                return f"Opening {pattern.split('open ')[-1].strip()}"
        
        # Handle ANY website - "open [anything]"
        match = re.search(r'open\s+(\S+)', command)
        if match:
            website = match.group(1).strip()
            # Clean up the website name
            if not website.startswith('http'):
                if '.' not in website:
                    website = website + '.com'
                website = 'https://www.' + website
            try:
                webbrowser.open(website)
                return f"Opening {match.group(1)}"
            except:
                # If fails, search on Google instead
                search_url = f"https://www.google.com/search?q={website}"
                webbrowser.open(search_url)
                return f"Searching for {website}"
        
        return None
    
    def _handle_system(self, command):
        """Handle system control commands"""
        for pattern, action in self.system_patterns.items():
            if re.search(pattern, command):
                if action == 'shutdown':
                    self.automation.shutdown()
                    return "Shutting down the system"
                elif action == 'restart':
                    self.automation.restart()
                    return "Restarting the system"
                elif action == 'sleep':
                    self.automation.sleep()
                    return "Putting system to sleep"
                elif action == 'lock':
                    self.automation.lock_screen()
                    return "Locking the screen"
        return None
    
    def _handle_music(self, command):
        """Handle music commands"""
        for pattern, action in self.music_patterns.items():
            match = re.search(pattern, command)
            if match:
                if action == 'play' and match.groups():
                    song = match.group(1)
                    result = self.music_library.play(song)
                    return result
                elif action == 'pause':
                    self.automation.media_control('pause')
                    return "Music paused"
                elif action == 'stop':
                    self.automation.media_control('stop')
                    return "Music stopped"
                elif action == 'next':
                    self.automation.media_control('next')
                    return "Playing next song"
                elif action == 'previous':
                    self.automation.media_control('previous')
                    return "Playing previous song"
        return None
    
    def _handle_volume(self, command):
        """Handle volume commands"""
        for pattern, action in self.volume_patterns.items():
            match = re.search(pattern, command)
            if match:
                if action[0] == 'volume':
                    if action[1] == 'up':
                        self.automation.volume_up()
                        return "Volume increased"
                    elif action[1] == 'down':
                        self.automation.volume_down()
                        return "Volume decreased"
                    elif action[1] == 'set' and match.groups():
                        level = int(match.group(1))
                        self.automation.set_volume(level)
                        return f"Volume set to {level} percent"
                    elif action[1] == 'mute':
                        self.automation.mute()
                        return "Volume muted"
        return None
    
    def _handle_apps(self, command):
        """Handle application opening commands"""
        for pattern, app in self.app_patterns.items():
            if re.search(pattern, command):
                self.automation.open_app(app)
                return f"Opening {app}"
        return None
    
    def _handle_info(self, command):
        """Handle information commands"""
        for pattern, info_type in self.info_patterns.items():
            if re.search(pattern, command):
                if info_type == 'time':
                    return f"The current time is {datetime.now().strftime('%I:%M %p')}"
                elif info_type == 'date':
                    return f"Today is {datetime.now().strftime('%B %d, %Y')}"
                elif info_type == 'day':
                    return f"It's {datetime.now().strftime('%A')}"
                elif info_type == 'weather':
                    if self.weather:
                        return self.weather.get_weather_description()
                    return self.automation.get_weather()
                elif info_type == 'aqi':
                    if self.weather:
                        return self.weather.get_aqi_description()
                    return "AQI information is available with the enhanced weather module."
                elif info_type == 'news':
                    return self.automation.get_news()
        return None
    
    def _handle_tasks(self, command):
        """Handle task management commands"""
        for pattern, action in self.task_patterns.items():
            match = re.search(pattern, command)
            if match:
                if action == 'add_task' and match.groups():
                    task = match.group(1)
                    self.memory.add_task(task)
                    return f"Added '{task}' to your todo list"
                elif action == 'show_tasks':
                    tasks = self.memory.get_tasks()
                    if tasks:
                        return "Your tasks are: " + ", ".join([f"{i+1}. {t}" for i, t in enumerate(tasks)])
                    else:                        return "Your todo list is empty"
                elif action == 'set_alarm' and match.groups():
                    time_str = match.group(1)
                    self.memory.set_alarm(time_str)
                    return f"Alarm set for {time_str}"
                elif action == 'set_reminder' and match.groups():
                    reminder = match.group(1)
                    self.memory.set_reminder(reminder)
                    return f"Reminder set for {reminder}"
        return None
    
    def _handle_whatsapp(self, command):
        """Handle WhatsApp commands"""
        if 'whatsapp' in command or 'send message' in command:
            # Extract name and message
            match = re.search(r'send\s+(?:message\s+)?(?:to\s+)?(\w+)\s+(?:that\s+)?(.+)', command)
            if match:
                name = match.group(1)
                message = match.group(2)
                self.automation.send_whatsapp(name, message)
                return f"Sending WhatsApp message to {name}"
        return None
    
    def _handle_search(self, command):
        """Handle internet search commands"""
        if 'search for' in command or 'search' in command:
            query = command.replace('search for', '').replace('search', '').strip()
            if query:
                self.automation.internet_search(query)
                return f"Searching for {query}"
        return None
    
    def _handle_memory(self, command):
        """Handle memory/remember commands"""
        for pattern, action in self.memory_patterns.items():
            match = re.search(pattern, command)
            if match:
                if action == 'remember' and match.groups():
                    # Store the memory
                    memory_text = match.group(1).strip()
                    # Store with timestamp
                    from datetime import datetime
                    self.user_memories[memory_text] = datetime.now().isoformat()
                    # Also save to memory module
                    self.memory.set_preference('last_memory', memory_text)
                    return f"I'll remember that: {memory_text}"
                elif action == 'what_remember':
                    # Get stored memories
                    last = self.memory.get_preference('last_memory')
                    if last:
                        return f"I remember: {last}"
                    return "I don't have any memories stored yet. Say 'Remember that' followed by something to store it."
                elif action == 'forget':
                    self.user_memories = {}
                    self.memory.set_preference('last_memory', '')
                    return "I've forgotten everything. My memory is now clear."
        return None
    
    def _handle_ai_conversation(self, command):
        """Handle AI conversation (fallback)"""
        # Check if it looks like a conversation rather than a command
        conversation_indicators = [
            'what', 'how', 'why', 'when', 'who', 'can you', 'tell me',
            'explain', 'what do you', 'what are', 'i want', 'i need',
            'help me', 'do you', 'are you', 'hello', 'hi', 'hey'
        ]
        
        is_conversation = any(indicator in command for indicator in conversation_indicators)
        
        # Also check if it's not a direct command
        command_indicators = ['open', 'play', 'start', 'stop', 'close', 'set', 'add', 'create']
        is_command = any(command.startswith(indicator) for indicator in command_indicators)
        
        if is_conversation and not is_command:
            response = self.ai_brain.get_response(command)
            self.memory.add_to_history('ai', response)
            return response
        
        # Smart Web Mode - If command not recognized, search on Google
        try:
            search_query = command.strip()
            self.automation.internet_search(search_query)
            return f"I couldn't find a command for that, but I searched for: {search_query}"
        except:
            return "I'm not sure how to help with that. Could you try rephrasing?"
