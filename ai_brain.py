"""
AI Brain Module for KARMA AI
Handles intelligent conversations using OpenAI or Google Gemini
"""

import logging
import os
import json
from datetime import datetime


class AIBrain:
    """
    AI Brain for KARMA AI
    Integrates with OpenAI GPT or Google Gemini for intelligent responses
    """
    
    def __init__(self, memory=None):
        """Initialize AI brain"""
        self.logger = logging.getLogger('KARMA-AIBrain')
        self.memory = memory
        
        # API Configuration - Using Gemini by default as per user request
        self.use_openai = False
        self.use_gemini = True
        
        # Load API keys - Using user's Gemini API key
        self.openai_api_key = os.environ.get('OPENAI_API_KEY', '')
        self.gemini_api_key = 'AIzaSyCUAQrdpjRqjlAuOH-fFkWckWvRnKeDmwg'
        
        # System prompt for personality
        self.system_prompt = """You are KARMA, an advanced AI personal assistant inspired by JARVIS from Iron Man. 
You are helpful, intelligent, and friendly. You have a sense of humor but remain professional.
You assist with various tasks including:
- Answering questions
- Having conversations
- Providing information
- Helping with tasks

Keep responses concise and natural. Use a conversational tone."""
        
        # Initialize clients if API keys are available
        self.openai_client = None
        self.gemini_client = None
        
        self._initialize_clients()
        
        self.logger.info("AI Brain initialized")
    
    def _initialize_clients(self):
        """Initialize AI API clients"""
        # OpenAI
        if self.openai_api_key:
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=self.openai_api_key)
                self.logger.info("OpenAI client initialized")
            except Exception as e:
                self.logger.warning(f"OpenAI initialization failed: {e}")
        
        # Gemini - Try different import methods for compatibility
        if self.gemini_api_key:
            try:
                # Try the new google.genai approach
                from google import genai
                self.gemini_client = genai.Client(api_key=self.gemini_api_key)
                self.logger.info("Gemini client initialized (new API)")
            except ImportError:
                try:
                    # Try google.generativeai (older approach)
                    import google.generativeai as gemini
                    gemini.configure(api_key=self.gemini_api_key)
                    self.gemini_model = gemini.GenerativeModel('gemini-pro')
                    self.logger.info("Gemini client initialized (legacy API)")
                except ImportError:
                    self.logger.warning("Gemini initialization failed: google-generativeai not installed")
    
    def get_response(self, user_input):
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
                self.logger.error(f"Gemini error: {e}")
        
        # Try OpenAI as fallback
        if self.openai_client:
            try:
                return self._get_openai_response(user_input, context)
            except Exception as e:
                self.logger.error(f"OpenAI error: {e}")
        
        # Fallback to rule-based responses
        return self._fallback_response(user_input)
    
    def _get_openai_response(self, user_input, context):
        """Get response from OpenAI"""
        # Build messages
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Add context (last 10 messages)
        for msg in context[-10:]:
            messages.append(msg)
        
        # Add current input
        messages.append({"role": "user", "content": user_input})
        
        # Get response
        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    def _get_gemini_response(self, user_input, context):
        """Get response from Google Gemini"""
        # Build context string
        context_str = ""
        for msg in context[-5:]:
            context_str += f"{msg['role']}: {msg['content']}\n"
        
        prompt = f"{self.system_prompt}\n\n{context_str}User: {user_input}\nKARMA:"
        
        response = self.gemini_client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt
        )
        return response.text
    
    def _fallback_response(self, user_input):
        """Fallback rule-based responses"""
        user_input = user_input.lower()
        
        # Common queries
        fallbacks = {
            'hello': "Hello! I'm KARMA, your personal AI assistant. How can I help you today?",
            'hi': "Hi there! How can I assist you?",
            'hey': "Hey! I'm listening. What would you like me to do?",
            'how are you': "I'm doing great! Ready to help you with anything you need.",
            'who are you': "I'm KARMA, your personal AI assistant inspired by JARVIS from Iron Man. I can help you with tasks, answer questions, and have conversations.",
            'what can you do': "I can do many things! I can answer questions, open apps, play music, control your system, send messages, search the web, and have conversations. Just ask!",
            'thank you': "You're welcome! Is there anything else I can help you with?",
            'thanks': "You're welcome! Happy to help!",
            'bye': "Goodbye! Feel free to call me anytime. Say 'Hey Karma' to activate me!",
            'goodbye': "Goodbye! Have a great day!",
            'help': "I can help you with: opening websites, playing music, controlling system functions, sending messages, searching the web, answering questions, and more. Just tell me what you need!",
            'time': f"The current time is {datetime.now().strftime('%I:%M %p')}",
            'date': f"Today is {datetime.now().strftime('%B %d, %Y')}",
        }
        
        for key, response in fallbacks.items():
            if key in user_input:
                return response
        
        # Default fallback
        return "I'm here to help! Could you please rephrase that or try a different command?"
    
    def set_api_key(self, provider, api_key):
        """
        Set API key for AI provider
        
        Args:
            provider: 'openai' or 'gemini'
            api_key: API key string
        """
        if provider.lower() == 'openai':
            self.openai_api_key = api_key
            os.environ['OPENAI_API_KEY'] = api_key
            self._initialize_clients()
        elif provider.lower() == 'gemini':
            self.gemini_api_key = api_key
            os.environ['GEMINI_API_KEY'] = api_key
            self._initialize_clients()
    
    def is_configured(self):
        """Check if AI is properly configured"""
        return bool(self.openai_client or self.gemini_client)
    
    def get_status(self):
        """Get AI configuration status"""
        return {
            'openai': bool(self.openai_client),
            'gemini': bool(self.gemini_client),
            'configured': self.is_configured()
        }
