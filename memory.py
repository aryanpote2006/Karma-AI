"""
Memory Module for KARMA AI
Handles conversation history, tasks, reminders, and persistent storage
"""

import os
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path


class Memory:
    """
    Memory management for KARMA AI
    - Conversation history
    - Task/todo management
    - Reminders and alarms
    - User preferences
    """
    
    def __init__(self, data_dir=None):
        """Initialize memory module"""
        self.logger = logging.getLogger('KARMA-Memory')
        
        # Data directory
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(__file__), 'data')
        
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # File paths
        self.conversation_file = self.data_dir / 'conversation.json'
        self.tasks_file = self.data_dir / 'tasks.json'
        self.reminders_file = self.data_dir / 'reminders.json'
        self.preferences_file = self.data_dir / 'preferences.json'
        
        # Load data
        self.conversation_history = self._load_json(self.conversation_file)
        self.tasks = self._load_json(self.tasks_file)
        self.reminders = self._load_json(self.reminders_file)
        self.preferences = self._load_json(self.preferences_file)
        
        # Initialize defaults
        if not self.conversation_history:
            self.conversation_history = []
        if not self.tasks:
            self.tasks = []
        if not self.reminders:
            self.reminders = []
        if not self.preferences:
            self.preferences = self._default_preferences()
        
        self.logger.info("Memory module initialized")
    
    def _default_preferences(self):
        """Get default preferences"""
        return {
            'name': 'User',
            'language': 'en',
            'voice_rate': 175,
            'voice_volume': 1.0,
            'wake_word': 'hey karma',
            'auto_start': False,
            'dark_mode': True,
            'notifications_enabled': True,
        }
    
    def _load_json(self, filepath):
        """Load JSON data from file"""
        try:
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading {filepath}: {e}")
        return None
    
    def _save_json(self, filepath, data):
        """Save data to JSON file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            self.logger.error(f"Error saving {filepath}: {e}")
            return False
    
    # ==================== Conversation History ====================
    
    def add_to_history(self, role, content):
        """
        Add message to conversation history
        
        Args:
            role: 'user' or 'ai'
            content: Message content
        """
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        
        self.conversation_history.append(message)
        
        # Keep only last 100 messages
        if len(self.conversation_history) > 100:
            self.conversation_history = self.conversation_history[-100:]
        
        # Save to file
        self._save_json(self.conversation_file, self.conversation_history)
    
    def get_conversation_history(self, limit=20):
        """Get recent conversation history"""
        return self.conversation_history[-limit:]
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        self._save_json(self.conversation_file, [])
        self.logger.info("Conversation history cleared")
    
    # ==================== Tasks ====================
    
    def add_task(self, task, due_date=None, priority='normal'):
        """
        Add a task to the todo list
        
        Args:
            task: Task description
            due_date: Optional due date
            priority: 'low', 'normal', or 'high'
        """
        task_obj = {
            'id': len(self.tasks) + 1,
            'task': task,
            'due_date': due_date,
            'priority': priority,
            'completed': False,
            'created_at': datetime.now().isoformat()
        }
        
        self.tasks.append(task_obj)
        self._save_json(self.tasks_file, self.tasks)
        
        self.logger.info(f"Task added: {task}")
        return task_obj['id']
    
    def get_tasks(self, include_completed=False):
        """Get all tasks"""
        if include_completed:
            return self.tasks
        return [t for t in self.tasks if not t.get('completed', False)]
    
    def complete_task(self, task_id):
        """Mark task as completed"""
        for task in self.tasks:
            if task['id'] == task_id:
                task['completed'] = True
                task['completed_at'] = datetime.now().isoformat()
                self._save_json(self.tasks_file, self.tasks)
                self.logger.info(f"Task completed: {task['task']}")
                return True
        return False
    
    def remove_task(self, task_id):
        """Remove a task"""
        self.tasks = [t for t in self.tasks if t['id'] != task_id]
        self._save_json(self.tasks_file, self.tasks)
        self.logger.info(f"Task removed: {task_id}")
    
    def clear_completed_tasks(self):
        """Clear all completed tasks"""
        self.tasks = [t for t in self.tasks if not t.get('completed', False)]
        self._save_json(self.tasks_file, self.tasks)
    
    # ==================== Reminders & Alarms ====================
    
    def set_reminder(self, reminder, time=None, date=None):
        """
        Set a reminder
        
        Args:
            reminder: Reminder message
            time: Time string (e.g., '14:30')
            date: Date string (e.g., '2024-12-25')
        """
        reminder_obj = {
            'id': len(self.reminders) + 1,
            'reminder': reminder,
            'time': time,
            'date': date,
            'triggered': False,
            'created_at': datetime.now().isoformat()
        }
        
        self.reminders.append(reminder_obj)
        self._save_json(self.reminders_file, self.reminders)
        
        self.logger.info(f"Reminder set: {reminder}")
        return reminder_obj['id']
    
    def set_alarm(self, time_str, message="Alarm"):
        """Set an alarm"""
        return self.set_reminder(message, time=time_str)
    
    def get_reminders(self):
        """Get all active reminders"""
        return [r for r in self.reminders if not r.get('triggered', False)]
    
    def check_reminders(self):
        """Check for due reminders"""
        now = datetime.now()
        due_reminders = []
        
        for reminder in self.reminders:
            if reminder.get('triggered', False):
                continue
            
            # Check time
            if reminder.get('time'):
                try:
                    reminder_time = datetime.strptime(reminder['time'], '%H:%M').time()
                    if reminder_time == now.time():
                        due_reminders.append(reminder)
                        reminder['triggered'] = True
                except:
                    pass
        
        if due_reminders:
            self._save_json(self.reminders_file, self.reminders)
        
        return due_reminders
    
    def delete_reminder(self, reminder_id):
        """Delete a reminder"""
        self.reminders = [r for r in self.reminders if r['id'] != reminder_id]
        self._save_json(self.reminders_file, self.reminders)
    
    # ==================== Preferences ====================
    
    def get_preference(self, key, default=None):
        """Get a preference value"""
        return self.preferences.get(key, default)
    
    def set_preference(self, key, value):
        """Set a preference value"""
        self.preferences[key] = value
        self._save_json(self.preferences_file, self.preferences)
        self.logger.info(f"Preference set: {key} = {value}")
    
    def get_all_preferences(self):
        """Get all preferences"""
        return self.preferences
    
    # ==================== Schedule ====================
    
    def add_to_schedule(self, event, date, time=None, description=""):
        """Add event to schedule"""
        schedule_file = self.data_dir / 'schedule.json'
        schedule = self._load_json(schedule_file) or []
        
        event_obj = {
            'id': len(schedule) + 1,
            'event': event,
            'date': date,
            'time': time,
            'description': description,
            'created_at': datetime.now().isoformat()
        }
        
        schedule.append(event_obj)
        self._save_json(schedule_file, schedule)
        
        self.logger.info(f"Event added to schedule: {event}")
        return event_obj['id']
    
    def get_schedule(self, date=None):
        """Get schedule for a specific date"""
        schedule_file = self.data_dir / 'schedule.json'
        schedule = self._load_json(schedule_file) or []
        
        if date:
            return [e for e in schedule if e.get('date') == date]
        return schedule
    
    def get_today_schedule(self):
        """Get today's schedule"""
        today = datetime.now().strftime('%Y-%m-%d')
        return self.get_schedule(today)
    
    # ==================== Statistics ====================
    
    def get_stats(self):
        """Get usage statistics"""
        return {
            'total_conversations': len(self.conversation_history),
            'total_tasks': len(self.tasks),
            'completed_tasks': len([t for t in self.tasks if t.get('completed', False)]),
            'total_reminders': len(self.reminders),
            'active_reminders': len(self.get_reminders()),
        }
