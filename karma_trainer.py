"""
KARMA AI - Training and Intelligence Layer
Improves command understanding by mapping multiple phrases to existing commands
Uses TF-IDF vectorization with scikit-learn for natural language matching
"""

import os
import json
import logging
import re
from difflib import SequenceMatcher

# Try to import scikit-learn, fallback to simple matching if not available
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    print("scikit-learn not found. Using simple string matching for command recognition.")


class KarmaTrainer:
    """
    Training layer for KARMA AI
    Maps multiple phrasings to existing commands using NLP
    """
    
    def __init__(self, training_data_path=None, logger=None):
        """
        Initialize the Karma Trainer
        
        Args:
            training_data_path: Path to training_data.json (optional)
            logger: Logger instance (optional)
        """
        self.logger = logger or logging.getLogger('KARMA-Trainer')
        self.training_data_path = training_data_path or os.path.join(
            os.path.dirname(__file__), 'training_data.json'
        )
        
        # Command mappings (phrase -> command)
        self.phrase_to_command = {}
        
        # All training phrases for TF-IDF
        self.training_phrases = []
        self.training_commands = []
        
        # Vectorizer (if sklearn available)
        self.vectorizer = None
        self.command_vectors = None
        
        # Unknown command message
        self.unknown_message = "I didn't understand that. Please say it again clearly."
        
        # Load training data
        self._load_training_data()
        
        if HAS_SKLEARN:
            self._build_vectorizer()
        
        self.logger.info(f"KarmaTrainer initialized with {len(self.phrase_to_command)} phrase mappings")
    
    def _load_training_data(self):
        """Load training data from JSON file"""
        try:
            if os.path.exists(self.training_data_path):
                with open(self.training_data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Build phrase to command mapping
                for command, phrases in data.items():
                    for phrase in phrases:
                        self.phrase_to_command[phrase.lower().strip()] = command
                        self.training_phrases.append(phrase.lower().strip())
                        self.training_commands.append(command)
                
                self.logger.info(f"Loaded {len(self.training_phrases)} training phrases")
            else:
                self.logger.warning(f"Training data file not found: {self.training_data_path}")
        except Exception as e:
            self.logger.error(f"Error loading training data: {e}")
    
    def _build_vectorizer(self):
        """Build TF-IDF vectorizer for semantic matching"""
        if not HAS_SKLEARN or not self.training_phrases:
            return
        
        try:
            self.vectorizer = TfidfVectorizer(
                ngram_range=(1, 2),  # Use unigrams and bigrams
                lowercase=True,
                analyzer='word'
            )
            self.command_vectors = self.vectorizer.fit_transform(self.training_phrases)
            self.logger.info("TF-IDF vectorizer built successfully")
        except Exception as e:
            self.logger.error(f"Error building vectorizer: {e}")
            self.vectorizer = None
    
    def train(self, command, phrases):
        """
        Add new training examples
        
        Args:
            command: The canonical command name
            phrases: List of phrase variations
        """
        for phrase in phrases:
            phrase = phrase.lower().strip()
            self.phrase_to_command[phrase] = command
            self.training_phrases.append(phrase)
            self.training_commands.append(command)
        
        # Rebuild vectorizer if available
        if HAS_SKLEARN and self.vectorizer:
            try:
                self.command_vectors = self.vectorizer.fit_transform(self.training_phrases)
            except Exception as e:
                self.logger.error(f"Error rebuilding vectorizer: {e}")
        
        self.logger.info(f"Added {len(phrases)} phrases for command: {command}")
    
    def save_training_data(self):
        """Save current training data to JSON file"""
        # Group phrases by command
        command_phrases = {}
        for phrase, command in self.phrase_to_command.items():
            if command not in command_phrases:
                command_phrases[command] = []
            command_phrases[command].append(phrase)
        
        try:
            with open(self.training_data_path, 'w', encoding='utf-8') as f:
                json.dump(command_phrases, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Training data saved to {self.training_data_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving training data: {e}")
            return False
    
    def predict_command(self, user_input):
        """
        Predict the canonical command from user input
        
        Args:
            user_input: Raw voice input from user
            
        Returns:
            tuple: (command, confidence) or (None, 0) if not recognized
        """
        if not user_input:
            return None, 0
        
        # Clean input
        user_input = user_input.lower().strip()
        
        # 1. First, try exact match
        if user_input in self.phrase_to_command:
            return self.phrase_to_command[user_input], 1.0
        
        # 2. Try partial match (input contains phrase)
        for phrase, command in self.phrase_to_command.items():
            if phrase in user_input or user_input in phrase:
                return command, 0.9
        
        # 3. Try fuzzy matching
        best_match = None
        best_score = 0
        
        for phrase, command in self.phrase_to_command.items():
            score = self._calculate_similarity(user_input, phrase)
            if score > best_score:
                best_score = score
                best_match = command
        
        # If similarity is above threshold, return the match
        if best_score > 0.6:
            return best_match, best_score
        
        # 4. Use TF-IDF if available
        if HAS_SKLEARN and self.vectorizer and self.command_vectors is not None:
            try:
                input_vector = self.vectorizer.transform([user_input])
                similarities = cosine_similarity(input_vector, self.command_vectors)[0]
                
                best_idx = similarities.argmax()
                best_tfidf_score = similarities[best_idx]
                
                if best_tfidf_score > 0.3:
                    return self.training_commands[best_idx], best_tfidf_score
            except Exception as e:
                self.logger.error(f"TF-IDF matching error: {e}")
        
        # No match found
        return None, 0
    
    def _calculate_similarity(self, s1, s2):
        """Calculate similarity between two strings"""
        # Direct sequence matching
        ratio = SequenceMatcher(None, s1, s2).ratio()
        
        # Word-based similarity
        words1 = set(s1.split())
        words2 = set(s2.split())
        
        if words1 and words2:
            word_overlap = len(words1.intersection(words2)) / max(len(words1), len(words2))
            # Combine scores
            return max(ratio, word_overlap)
        
        return ratio
    
    def recognize(self, user_input):
        """
        Main entry point - recognize command from user voice input
        
        Args:
            user_input: Raw voice input string
            
        Returns:
            str: Canonical command name if recognized, None otherwise
        """
        command, confidence = self.predict_command(user_input)
        
        if command:
            self.logger.info(f"Recognized: '{user_input}' -> '{command}' (confidence: {confidence:.2f})")
            return command
        else:
            self.logger.info(f"Could not recognize: '{user_input}'")
            return None
    
    def get_unknown_message(self):
        """Get the message for unrecognized commands"""
        return self.unknown_message


# Standalone function for simple integration
def process_voice_input(user_input, trainer=None):
    """
    Process voice input and return canonical command
    
    Args:
        user_input: Raw voice input string
        trainer: KarmaTrainer instance (optional, will create if None)
        
    Returns:
        str: Canonical command name, or None if not recognized
    """
    if trainer is None:
        trainer = KarmaTrainer()
    
    return trainer.recognize(user_input)


# Command to canonical command mapping for the original code
# These are the actual command strings that karma.py and command_processor.py expect
COMMAND_MAPPING = {
    # Website commands
    'open_youtube': 'open youtube',
    'open_google': 'open google',
    'open_facebook': 'open facebook',
    'open_instagram': 'open instagram',
    'open_twitter': 'open twitter',
    'open_linkedin': 'open linkedin',
    'open_github': 'open github',
    'open_gmail': 'open gmail',
    'open_whatsapp': 'open whatsapp',
    'open_netflix': 'open netflix',
    'open_amazon': 'open amazon',
    'open_chatgpt': 'open chatgpt',
    'open_gemini': 'open gemini ai',
    'open_maps': 'open maps',
    'open_calendar': 'open calendar',
    'open_drive': 'open drive',
    'open_docs': 'open docs',
    'open_meet': 'open meet',
    'open_zoom': 'open zoom',
    'open_spotify': 'open spotify',
    'open_notes': 'open notes',
    'open_news': 'open news',
    'open_camera': 'open camera',
    'open_weather': 'open weather',
    'open_dictionary': 'open dictionary',
    'open_hotstar': 'open hotstar',
    'open_classroom': 'open classroom',
    'open_photos': 'open photos',
    
    # App commands
    'open_chrome': 'open chrome',
    'open_vscode': 'open vs code',
    'open_notepad': 'open notepad',
    'open_calculator': 'open calculator',
    'open_word': 'open word',
    'open_excel': 'open excel',
    'open_powerpoint': 'open powerpoint',
    'open_command_prompt': 'open command prompt',
    'open_file_explorer': 'open file explorer',
    'open_task_manager': 'open task manager',
    'open_control_panel': 'open control panel',
    
    # Music commands
    'play_music': 'play',
    'pause_music': 'pause',
    'stop_music': 'stop music',
    'next_song': 'next song',
    'previous_song': 'previous song',
    'play_bollywood': 'play bollywood',
    'play_popular': 'play popular',
    'play_relaxing': 'play relaxing',
    'play_classical': 'play classical',
    'play_workout': 'play workout',
    
    # Volume commands
    'volume_up': 'volume up',
    'volume_down': 'volume down',
    'mute': 'mute',
    
    # System commands
    'shutdown': 'shutdown pc',
    'restart': 'restart pc',
    'sleep': 'sleep pc',
    'lock': 'lock pc',
    
    # Info commands
    'get_time': 'what is the time',
    'get_date': 'what is the date',
    'get_weather': 'what is the weather',
    'get_aqi': 'air quality',
    
    # Task commands
    'add_task': 'add task',
    'show_tasks': 'show tasks',
    
    # Memory commands
    'remember': 'remember that',
    'what_remember': 'what do you remember',
    
    # YouTube commands
    'play_youtube': 'play on youtube',
    'search_youtube': 'search youtube',
    
    # Other commands
    'voice_typing': 'voice typing',
    'list_songs': 'list songs',
    'open_music': 'open music',
}


def get_command_string(canonical_name):
    """
    Get the actual command string for karma.py
    
    Args:
        canonical_name: The canonical command name from trainer
        
    Returns:
        str: The command string to pass to original code
    """
    return COMMAND_MAPPING.get(canonical_name, canonical_name)


# Global trainer instance (lazy initialization)
_trainer_instance = None


def get_trainer():
    """Get or create the global trainer instance"""
    global _trainer_instance
    if _trainer_instance is None:
        _trainer_instance = KarmaTrainer()
    return _trainer_instance


if __name__ == "__main__":
    # Test the trainer
    print("KARMA AI Trainer - Testing Mode")
    print("=" * 50)
    
    trainer = KarmaTrainer()
    
    # Test phrases
    test_phrases = [
        "start youtube",
        "launch youtube",
        "play youtube",
        "open google search",
        "what time is it now",
        "increase volume",
        "turn up the volume",
        "shutdown my computer",
    ]
    
    print("\nTesting phrase recognition:")
    for phrase in test_phrases:
        result = trainer.recognize(phrase)
        print(f"  '{phrase}' -> '{result}'")
    
    print("\n" + "=" * 50)
    print("Trainer is ready for integration!")

