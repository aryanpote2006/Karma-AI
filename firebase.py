"""
Firebase Module for KARMA ULTRA PRO
Handles cloud storage, command history, conversation logs, and user profiles
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path

# Try to import firebase-admin, fallback to local storage if not available
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    logging.warning("Firebase not available, using local storage fallback")


class FirebaseManager:
    """
    Firebase Cloud Integration for KARMA AI
    Stores:
    - Command history
    - Conversation logs with timestamps
    - User profiles and preferences
    - Location tracking data
    - Usage analytics
    """
    
    def __init__(self, credentials_path=None, logger=None):
        """Initialize Firebase connection"""
        self.logger = logger or logging.getLogger('KARMA-Firebase')
        self.credentials_path = credentials_path
        self.db = None
        self.use_firebase = False
        self.user_id = "default_user"
        
        # Local fallback storage
        self.local_storage_dir = Path(__file__).parent / 'data' / 'cloud'
        self.local_storage_dir.mkdir(parents=True, exist_ok=True)
        
        self._initialize_firebase()
        
        self.logger.info("Firebase Manager initialized")
    
    def _initialize_firebase(self):
        """Initialize Firebase connection"""
        if not FIREBASE_AVAILABLE:
            self.logger.info("Using local storage fallback")
            return
        
        # Check for credentials
        if self.credentials_path and os.path.exists(self.credentials_path):
            try:
                cred = credentials.Certificate(self.credentials_path)
                firebase_admin.initialize_app(cred)
                self.db = firestore.client()
                self.use_firebase = True
                self.logger.info("Firebase connected successfully")
                return
            except Exception as e:
                self.logger.error(f"Firebase init error: {e}")
        
        # Try environment variable for credentials
        firebase_creds = os.environ.get('FIREBASE_CREDENTIALS')
        if firebase_creds:
            try:
                import io
                cred_dict = json.loads(firebase_creds)
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred)
                self.db = firestore.client()
                self.use_firebase = True
                self.logger.info("Firebase connected (from env)")
                return
            except Exception as e:
                self.logger.error(f"Firebase env error: {e}")
        
        # Fallback to local storage
        self.logger.info("Using local storage fallback")
        self.use_firebase = False
    
    def set_user(self, user_id):
        """Set current user ID"""
        self.user_id = user_id
    
    # ==================== Command History ====================
    
    def save_command(self, command, response, command_type="general"):
        """
        Save command to history
        
        Args:
            command: User's command
            response: AI's response
            command_type: Type of command (voice, text, api)
        """
        timestamp = datetime.now().isoformat()
        
        command_data = {
            'command': command,
            'response': response,
            'type': command_type,
            'timestamp': timestamp,
            'user_id': self.user_id
        }
        
        if self.use_firebase and self.db:
            try:
                self.db.collection('command_history').add(command_data)
            except Exception as e:
                self.logger.error(f"Firebase save error: {e}")
                self._save_locally('commands', command_data)
        else:
            self._save_locally('commands', command_data)
    
    def get_command_history(self, limit=50):
        """Get command history"""
        if self.use_firebase and self.db:
            try:
                docs = self.db.collection('command_history') \
                    .where('user_id', '==', self.user_id) \
                    .order_by('timestamp', direction=firestore.Query.DESCENDING) \
                    .limit(limit) \
                    .stream()
                
                return [{'id': doc.id, **doc.to_dict()} for doc in docs]
            except Exception as e:
                self.logger.error(f"Firebase fetch error: {e}")
        
        return self._load_locally('commands', limit)
    
    # ==================== Conversation Logs ====================
    
    def save_conversation(self, user_message, ai_message):
        """
        Save conversation exchange
        
        Args:
            user_message: User's message
            ai_message: AI's response
        """
        timestamp = datetime.now().isoformat()
        
        conversation_data = {
            'user_message': user_message,
            'ai_message': ai_message,
            'timestamp': timestamp,
            'user_id': self.user_id
        }
        
        if self.use_firebase and self.db:
            try:
                self.db.collection('conversations').add(conversation_data)
            except Exception as e:
                self.logger.error(f"Firebase conv error: {e}")
                self._save_locally('conversations', conversation_data)
        else:
            self._save_locally('conversations', conversation_data)
    
    def get_conversations(self, limit=20):
        """Get conversation history"""
        if self.use_firebase and self.db:
            try:
                docs = self.db.collection('conversations') \
                    .where('user_id', '==', self.user_id) \
                    .order_by('timestamp', direction=firestore.Query.DESCENDING) \
                    .limit(limit) \
                    .stream()
                
                return [{'id': doc.id, **doc.to_dict()} for doc in docs]
            except Exception as e:
                self.logger.error(f"Firebase conv fetch error: {e}")
        
        return self._load_locally('conversations', limit)
    
    # ==================== User Profile ====================
    
    def save_user_profile(self, profile_data):
        """
        Save user profile
        
        Args:
            profile_data: Dictionary with user info
        """
        profile_data['updated_at'] = datetime.now().isoformat()
        
        if self.use_firebase and self.db:
            try:
                self.db.collection('users').document(self.user_id).set(profile_data, merge=True)
            except Exception as e:
                self.logger.error(f"Firebase profile save error: {e}")
                self._save_locally('profile', profile_data)
        else:
            self._save_locally('profile', profile_data)
    
    def get_user_profile(self):
        """Get user profile"""
        if self.use_firebase and self.db:
            try:
                doc = self.db.collection('users').document(self.user_id).get()
                if doc.exists:
                    return doc.to_dict()
            except Exception as e:
                self.logger.error(f"Firebase profile fetch error: {e}")
        
        return self._load_locally('profile')
    
    def update_user_preference(self, key, value):
        """Update a single user preference"""
        profile = self.get_user_profile() or {}
        profile[key] = value
        self.save_user_profile(profile)
    
    # ==================== Location Tracking ====================
    
    def save_location(self, latitude, longitude, location_name=None):
        """
        Save user location
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            location_name: Optional location name
        """
        location_data = {
            'latitude': latitude,
            'longitude': longitude,
            'location_name': location_name,
            'timestamp': datetime.now().isoformat(),
            'user_id': self.user_id
        }
        
        if self.use_firebase and self.db:
            try:
                self.db.collection('locations').add(location_data)
            except Exception as e:
                self.logger.error(f"Firebase location error: {e}")
                self._save_locally('locations', location_data)
        else:
            self._save_locally('locations', location_data)
    
    def get_last_location(self):
        """Get last known location"""
        if self.use_firebase and self.db:
            try:
                docs = self.db.collection('locations') \
                    .where('user_id', '==', self.user_id) \
                    .order_by('timestamp', direction=firestore.Query.DESCENDING) \
                    .limit(1) \
                    .stream()
                
                for doc in docs:
                    return doc.to_dict()
            except Exception as e:
                self.logger.error(f"Firebase location fetch error: {e}")
        
        locations = self._load_locally('locations', 1)
        return locations[0] if locations else None
    
    # ==================== Analytics ====================
    
    def log_event(self, event_type, event_data=None):
        """
        Log analytics event
        
        Args:
            event_type: Type of event
            event_data: Additional event data
        """
        event = {
            'event_type': event_type,
            'event_data': event_data or {},
            'timestamp': datetime.now().isoformat(),
            'user_id': self.user_id
        }
        
        if self.use_firebase and self.db:
            try:
                self.db.collection('analytics').add(event)
            except Exception as e:
                self.logger.error(f"Firebase analytics error: {e}")
        else:
            self._save_locally('analytics', event)
    
    def get_analytics(self, event_type=None, days=7):
        """Get analytics data"""
        if self.use_firebase and self.db:
            try:
                query = self.db.collection('analytics') \
                    .where('user_id', '==', self.user_id)
                
                if event_type:
                    query = query.where('event_type', '==', event_type)
                
                docs = query.order_by('timestamp', direction=firestore.Query.DESCENDING) \
                    .limit(100) \
                    .stream()
                
                return [{'id': doc.id, **doc.to_dict()} for doc in docs]
            except Exception as e:
                self.logger.error(f"Firebase analytics fetch error: {e}")
        
        return self._load_locally('analytics', 50)
    
    # ==================== Statistics ====================
    
    def get_statistics(self):
        """Get usage statistics"""
        commands = self.get_command_history(100)
        conversations = self.get_conversations(50)
        
        return {
            'total_commands': len(commands),
            'total_conversations': len(conversations),
            'last_command': commands[0] if commands else None,
            'last_conversation': conversations[0] if conversations else None,
            'user_id': self.user_id,
            'using_firebase': self.use_firebase
        }
    
    # ==================== Local Storage Fallback ====================
    
    def _save_locally(self, collection, data):
        """Save data locally as JSON"""
        try:
            filepath = self.local_storage_dir / f"{collection}.json"
            
            # Load existing data
            existing = []
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
            
            # Add new data
            existing.append(data)
            
            # Keep last 500 items
            if len(existing) > 500:
                existing = existing[-500:]
            
            # Save
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(existing, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Local save error: {e}")
    
    def _load_locally(self, collection, limit=None):
        """Load data from local storage"""
        try:
            filepath = self.local_storage_dir / f"{collection}.json"
            
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Return reversed (newest first)
                result = list(reversed(data))
                
                if limit:
                    result = result[:limit]
                
                return result
                
        except Exception as e:
            self.logger.error(f"Local load error: {e}")
        
        return []
    
    # ==================== Utility ====================
    
    def clear_history(self):
        """Clear all history (local only for safety)"""
        if self.use_firebase:
            self.logger.warning("Cannot clear Firebase history programmatically")
            return
        
        for collection in ['commands', 'conversations', 'locations', 'analytics']:
            filepath = self.local_storage_dir / f"{collection}.json"
            if filepath.exists():
                filepath.unlink()
        
        self.logger.info("Local history cleared")
    
    def export_data(self):
        """Export all data as dictionary"""
        return {
            'commands': self.get_command_history(100),
            'conversations': self.get_conversations(50),
            'profile': self.get_user_profile(),
            'statistics': self.get_statistics()
        }


# Singleton instance
_firebase_manager = None

def get_firebase_manager(credentials_path=None, logger=None):
    """Get or create Firebase manager singleton"""
    global _firebase_manager
    if _firebase_manager is None:
        _firebase_manager = FirebaseManager(credentials_path, logger)
    return _firebase_manager
