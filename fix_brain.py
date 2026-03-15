"""Fix AI Brain to handle quota errors"""

# Read the file
with open('ai_brain.py', 'r') as f:
    content = f.read()

# Find and replace the get_response method
old_code = '''    def get_response(self, user_input):
        """
        Get AI response for user input
        
        Args:
            user_input: User's message
            
        Returns:
            AI response string
        """
        self.logger.info(f"Processing AI request: {user_input[:50]}...")
        
        # Get conversation context from memory
        context = self.memory.get_conversation_history() if self.memory else []
        
        # Try Gemini first (user's preference)
        if self.gemini_client:
            try:
                return self._get_gemini_response(user_input, context)
            except Exception as e:
                self.logger.error(f"Gemini error: {e}")'''

new_code = '''    def get_response(self, user_input):
        """
        Get AI response for user input
        
        Args:
            user_input: User's message
            
        Returns:
            AI response string
        """
        self.logger.info(f"Processing AI request: {user_input[:50]}...")
        
        # Get conversation context from memory
        context = self.memory.get_conversation_history() if self.memory else []
        
        # Try Gemini first (user's preference)
        if self.gemini_client:
            try:
                return self._get_gemini_response(user_input, context)
            except Exception as e:
                error_str = str(e)
                # Check for quota/rate limit errors
                if '429' in error_str or 'RESOURCE_EXHAUSTED' in error_str or 'quota' in error_str.lower():
                    self.logger.warning("Gemini API quota exceeded, using fallback")
                    return "I'm temporarily unable to connect to the AI service due to API limits. But I can still help you with commands like: opening websites, playing music, checking weather, and more!"
                self.logger.error(f"Gemini error: {e}")'''

content = content.replace(old_code, new_code)

# Write back
with open('ai_brain.py', 'w') as f:
    f.write(content)

print("Fixed ai_brain.py!")
