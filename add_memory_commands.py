"""Add Memory Commands to Command Processor"""

# Read the file
with open('command_processor.py', 'r') as f:
    content = f.read()

# Add memory patterns to task_patterns
old_patterns = '''        # Task commands
        self.task_patterns = {
            r'add\s+(?:to\s+)?(?:my\s+)?(todo|to-do|list)': 'add_task',
            r'show\s+(?:my\s+)?(todo|to-do|list)': 'show_tasks',
            r'remove\s+task\s+(\d+)': 'remove_task',
            r'complete\s+task\s+(\d+)': 'complete_task',
            r'set\s+(?:an\s+)?alarm\s+(.+)': 'set_alarm',
            r'set\s+reminder\s+(.+)': 'set_reminder',
            r'create\s+(?:a\s+)?schedule': 'create_schedule',
        }'''

new_patterns = '''        # Task commands
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
        }'''

content = content.replace(old_patterns, new_patterns)

# Add memory_patterns to __init__
old_init = '''        # Command patterns
        self._setup_command_patterns()'''
new_init = '''        # Command patterns
        self._setup_command_patterns()
        
        # Memory storage
        self.user_memories = {}'''

content = content.replace(old_init, new_init)

# Update the process method to handle memory commands
old_process = '''        # 10. Fallback to AI brain for conversation
        return self._handle_ai_conversation(command)'''

new_process = '''        # 10. Memory commands
        response = self._handle_memory(command)
        if response:
            return response
        
        # 11. Fallback to AI brain for conversation
        return self._handle_ai_conversation(command)'''

content = content.replace(old_process, new_process)

# Add _handle_memory method before _handle_ai_conversation
old_ai = '''    def _handle_ai_conversation(self, command):'''
new_ai = '''    def _handle_memory(self, command):
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
    
    def _handle_ai_conversation(self, command):'''

content = content.replace(old_ai, new_ai)

# Write back
with open('command_processor.py', 'w') as f:
    f.write(content)

print("Added memory commands to command_processor.py!")
