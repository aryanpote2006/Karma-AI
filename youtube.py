"""
YouTube Automation Module for KARMA ULTRA PRO
Voice-controlled YouTube playback and search
"""

import logging
import threading
import time
import webbrowser
import re
from datetime import datetime


class YouTubeController:
    """
    YouTube Automation for KARMA AI
    Features:
    - Play videos by voice command
    - Search YouTube
    - Control playback (play, pause, next, previous)
    - Get video information
    - Queue management
    """
    
    def __init__(self, logger=None):
        """Initialize YouTube controller"""
        self.logger = logger or logging.getLogger('KARMA-YouTube')
        
        # Playback state
        self.is_playing = False
        self.current_video = None
        self.video_queue = []
        self.search_results = []
        
        # Browser control
        self.browser = None
        
        self.logger.info("YouTube Controller initialized")
    
    def play_video(self, query):
        """
        Play a YouTube video
        
        Args:
            query: Video name or search query
            
        Returns:
            Response message
        """
        self.logger.info(f"Playing video: {query}")
        
        # Search for video
        video_url = self._search_video(query)
        
        if video_url:
            # Open in browser
            webbrowser.open(video_url)
            
            self.current_video = {
                'query': query,
                'url': video_url,
                'timestamp': datetime.now().isoformat()
            }
            self.is_playing = True
            
            return f"Playing {query} on YouTube"
        
        return f"Could not find video: {query}"
    
    def playPlaylist(self, playlist_name):
        """
        Play a YouTube playlist
        
        Args:
            playlist_name: Name of playlist
            
        Returns:
            Response message
        """
        self.logger.info(f"Playing playlist: {playlist_name}")
        
        # Search for playlist
        search_url = f"https://www.youtube.com/results?search_query={playlist_name.replace(' ', '+')}+playlist"
        webbrowser.open(search_url)
        
        return f"Searching for {playlist_name} playlist on YouTube"
    
    def search(self, query):
        """
        Search YouTube
        
        Args:
            query: Search query
            
        Returns:
            Response message with search results
        """
        self.logger.info(f"YouTube search: {query}")
        
        # Perform search
        search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        webbrowser.open(search_url)
        
        self.search_results = [
            {'query': query, 'url': search_url, 'timestamp': datetime.now().isoformat()}
        ]
        
        return f"Searching YouTube for {query}"
    
    def get_video_info(self, query):
        """
        Get video information
        
        Args:
            query: Video name
            
        Returns:
            Video information
        """
        # This would ideally use YouTube Data API
        # For now, return a description
        return f"Here's information about {query}. You can ask me to play it or search for more videos."
    
    def add_to_queue(self, video_name):
        """
        Add video to queue
        
        Args:
            video_name: Name of video
            
        Returns:
            Response message
        """
        self.video_queue.append({
            'name': video_name,
            'added_at': datetime.now().isoformat()
        })
        
        return f"Added {video_name} to queue"
    
    def play_next(self):
        """
        Play next video in queue
        
        Returns:
            Response message
        """
        if self.video_queue:
            next_video = self.video_queue.pop(0)
            return self.play_video(next_video['name'])
        
        return "Queue is empty. Add videos to queue or search for something to play."
    
    def show_queue(self):
        """
        Show current queue
        
        Returns:
            Queue information
        """
        if not self.video_queue:
            return "Your queue is empty"
        
        queue_text = "Your queue: "
        for i, video in enumerate(self.video_queue, 1):
            queue_text += f"{i}. {video['name']}, "
        
        return queue_text.rstrip(", ")
    
    def clear_queue(self):
        """
        Clear the queue
        
        Returns:
            Response message
        """
        self.video_queue = []
        return "Queue cleared"
    
    def _search_video(self, query):
        """
        Search for video URL (simplified)
        
        Args:
            query: Search query
            
        Returns:
            Video URL
        """
        # For full YouTube search, you would use the YouTube Data API
        # This is a simplified version that opens a search page
        return f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    
    def control_playback(self, action):
        """
        Control playback (requires browser automation)
        
        Args:
            action: 'play', 'pause', 'next', 'previous', 'mute', 'unmute'
            
        Returns:
            Response message
        """
        # Note: Browser automation requires additional libraries like selenium
        # For now, we'll use keyboard shortcuts via pyautogui
        
        try:
            import pyautogui
            
            if action == 'play' or action == 'pause':
                pyautogui.press('space')
                return "Toggled playback"
            elif action == 'next':
                # YouTube: Shift + N
                pyautogui.hotkey('shift', 'n')
                return "Skipped to next video"
            elif action == 'previous':
                # YouTube: Shift + P
                pyautogui.hotkey('shift', 'p')
                return "Played previous video"
            elif action == 'mute':
                pyautogui.press('m')
                return "Toggled mute"
            elif action == 'fullscreen':
                pyautogui.press('f')
                return "Toggled fullscreen"
            elif action == ' captions':
                pyautogui.press('c')
                return "Toggled captions"
                
        except ImportError:
            self.logger.warning("pyautogui not available for playback control")
        except Exception as e:
            self.logger.error(f"Playback control error: {e}")
        
        return "Playback control not available"
    
    def get_status(self):
        """
        Get current playback status
        
        Returns:
            Status dictionary
        """
        return {
            'is_playing': self.is_playing,
            'current_video': self.current_video,
            'queue_length': len(self.video_queue),
            'last_search': self.search_results[-1] if self.search_results else None
        }


# Singleton instance
_youtube_controller = None

def get_youtube_controller(logger=None):
    """Get or create YouTube controller singleton"""
    global _youtube_controller
    if _youtube_controller is None:
        _youtube_controller = YouTubeController(logger)
    return _youtube_controller
