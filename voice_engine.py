"""
Voice Engine Module for KARMA AI
Handles speech recognition and text-to-speech
"""

import speech_recognition as sr
import pyttsx3
import threading
import time
import logging


class VoiceEngine:
    """Handles all voice-related operations"""
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger('KARMA-Voice')
        
        # Thread locks
        self._tts_lock = threading.Lock()
        self._listen_lock = threading.Lock()
        
        # Speech recognizer
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 2500
        self.recognizer.pause_threshold = 0.6
        self.recognizer.phrase_threshold = 0.2
        self.recognizer.dynamic_energy_threshold = True
        
        # TTS engine
        self.engine = None
        self._init_tts()
        
        # Microphone
        self.microphone = None
        self._init_microphone()
        
        # State
        self.is_listening = False
        self.is_speaking = False
        self.stop_listening = False
        self.wake_word_detected = False
        
        # Callbacks
        self.audio_callback = None
        self.wake_word_callback = None
        self._stop_background = threading.Event()
        self.wake_word = "karma"
        
        self.logger.info("Voice Engine initialized")
    
    def _init_tts(self):
        """Initialize TTS engine"""
        try:
            self.engine = pyttsx3.init()
            voices = self.engine.getProperty('voices')
            for voice in voices:
                if 'english' in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    self.logger.info(f"Using voice: {voice.name}")
                    break
            self.engine.setProperty('rate', 175)
            self.engine.setProperty('volume', 1.0)
            self.logger.info("TTS engine initialized")
        except Exception as e:
            self.logger.error(f"TTS error: {e}")
            try:
                self.engine = pyttsx3.init()
            except:
                self.engine = None
    
    def _init_microphone(self):
        """Initialize microphone"""
        try:
            mic_list = sr.Microphone.list_microphone_names()
            self.logger.info(f"Available microphones: {len(mic_list)}")
            if mic_list:
                self.logger.info(f"Default mic: {mic_list[0]}")
            
            self.microphone = sr.Microphone()
            with self.microphone as source:
                self.logger.info("Calibrating microphone...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1.5)
                self.logger.info(f"Energy threshold: {self.recognizer.energy_threshold}")
        except OSError as e:
            self.logger.error(f"No microphone: {e}")
            self.microphone = None
        except Exception as e:
            self.logger.error(f"Mic error: {e}")
            self.microphone = None
    
    def speak(self, text, interrupt=False):
        """Convert text to speech - THREAD SAFE"""
        if not self.engine:
            self.logger.warning("TTS not available")
            return
        
        with self._tts_lock:
            self.is_speaking = True
            try:
                self.logger.info(f"Speaking: {text[:50]}...")
                if interrupt:
                    try:
                        self.engine.stop()
                    except:
                        pass
                self.engine.say(text)
                self.engine.runAndWait()
            except RuntimeError as e:
                self.logger.warning(f"TTS error: {e}")
                try:
                    time.sleep(0.1)
                    self.engine.say(text)
                    self.engine.runAndWait()
                except Exception as inner:
                    self.logger.error(f"TTS retry: {inner}")
            except Exception as e:
                self.logger.error(f"Speech error: {e}")
            finally:
                self.is_speaking = False
    
    def speak_async(self, text, interrupt=False):
        """Speak in separate thread"""
        thread = threading.Thread(target=self.speak, args=(text, interrupt), daemon=True)
        thread.start()
        time.sleep(0.05)
    
    def listen(self, timeout=None, phrase_time_limit=None):
        """Listen for speech"""
        with self._listen_lock:
            if not self.microphone:
                self.logger.error("No microphone")
                return None
            
            timeout = timeout if timeout else 5
            phrase_time_limit = phrase_time_limit if phrase_time_limit else 8
            
            try:
                source = self.microphone
                self.logger.info(f"Listening... (timeout: {timeout}s)")
                
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
                
                if audio:
                    self.logger.info("Recognizing...")
                    command = self.recognizer.recognize_google(audio, language="en-IN")
                    self.logger.info(f"Recognized: {command}")
                    return command.lower()
                return None
                
            except sr.WaitTimeoutError:
                self.logger.debug("No speech detected")
                return None
            except sr.UnknownValueError:
                self.logger.debug("Speech not understood")
                return None
            except sr.RequestError as e:
                self.logger.error(f"Recognition error: {e}")
                return None
            except Exception as e:
                self.logger.error(f"Listen error: {e}")
                return None
    
    def listen_for_command(self, timeout=5, phrase_time_limit=10):
        """Listen for command"""
        return self.listen(timeout=timeout, phrase_time_limit=phrase_time_limit)
    
    def start_continuous_listening(self, callback=None, wake_word="karma"):
        """Start continuous background listening"""
        self.audio_callback = callback
        self.wake_word = wake_word.lower() if wake_word else "karma"
        self.stop_listening = False
        self._stop_background.clear()
        
        self.recognizer.listen_in_background(
            self.microphone,
            self._audio_callback,
            phrase_time_limit=5
        )
        
        self.logger.info(f"Continuous listening started (wake word: {self.wake_word})")
    
    def _audio_callback(self, recognizer, audio):
        """Callback for background listening"""
        try:
            command = recognizer.recognize_google(audio, language="en-IN")
            command = command.lower()
            self.logger.debug(f"Background heard: {command}")
            
            # Check for wake word
            if self.wake_word in command:
                self.logger.info(f"Wake word detected: {command}")
                self.wake_word_detected = True
                
                # Call wake word callback with command as argument
                if self.wake_word_callback:
                    try:
                        # Try calling with command argument first
                        self.wake_word_callback(command)
                    except TypeError:
                        try:
                            # Fall back to calling without arguments
                            self.wake_word_callback()
                        except Exception as e2:
                            self.logger.error(f"Wake callback failed: {e2}")
                elif self.audio_callback:
                    self.audio_callback(command)
            else:
                if self.audio_callback:
                    self.audio_callback(command)
                    
        except sr.UnknownValueError:
            pass
        except sr.RequestError as e:
            self.logger.error(f"Background error: {e}")
        except Exception as e:
            self.logger.error(f"Callback error: {e}")
    
    def stop_continuous_listening(self):
        """Stop continuous listening"""
        self.stop_listening = True
        self._stop_background.set()
        self.logger.info("Continuous listening stopped")
    
    def stop(self):
        """Stop all voice operations"""
        self.stop_listening = True
        self._stop_background.set()
        if self.engine:
            try:
                self.engine.stop()
            except:
                pass
        self.logger.info("Voice engine stopped")
    
    def recognize_speech(self, audio_data=None):
        """Recognize speech from audio"""
        if audio_data is None:
            return self.listen()
        if isinstance(audio_data, str):
            return audio_data
        return None
    
    def set_voice_rate(self, rate):
        """Set speech rate"""
        if self.engine:
            self.engine.setProperty('rate', rate)
    
    def set_voice_volume(self, volume):
        """Set volume"""
        if self.engine:
            self.engine.setProperty('volume', volume)
    
    def get_available_voices(self):
        """Get available voices"""
        if self.engine:
            return self.engine.getProperty('voices')
        return []
    
    def set_voice(self, voice_id):
        """Set voice"""
        if self.engine:
            self.engine.setProperty('voice', voice_id)
    
    def recalibrate_microphone(self):
        """Re-calibrate microphone"""
        if self.microphone:
            try:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                    self.logger.info(f"Recalibrated. Threshold: {self.recognizer.energy_threshold}")
            except Exception as e:
                self.logger.error(f"Recalibration error: {e}")
    
    def set_energy_threshold(self, threshold):
        """Set energy threshold"""
        self.recognizer.energy_threshold = threshold
        self.logger.info(f"Threshold set to: {threshold}")
