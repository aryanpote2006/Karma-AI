"""
Automation Module for KARMA AI
Handles system automation, controls, and external service integrations
"""

import os
import sys
import subprocess
import logging
import time
import webbrowser
import requests
from datetime import datetime


class Automation:
    """
    Handles all automation tasks:
    - System controls (shutdown, restart, volume, brightness)
    - Application launching
    - File operations
    - Internet searches
    - WhatsApp messaging
    - Weather and news
    """
    
    def __init__(self, logger=None):
        """Initialize automation module"""
        self.logger = logger or logging.getLogger('KARMA-Automation')
        
        # Platform-specific imports
        self.is_windows = sys.platform == 'win32'
        
        self.logger.info("Automation module initialized")
    
    # ==================== System Controls ====================
    
    def shutdown(self, delay=0):
        """Shutdown the computer"""
        self.logger.info("Shutting down system...")
        if self.is_windows:
            subprocess.run(['shutdown', '/s', '/t', str(delay)], shell=False)
        else:
            subprocess.run(['shutdown', '+0'], shell=False)
    
    def restart(self, delay=0):
        """Restart the computer"""
        self.logger.info("Restarting system...")
        if self.is_windows:
            subprocess.run(['shutdown', '/r', '/t', str(delay)], shell=False)
        else:
            subprocess.run(['reboot'], shell=False)
    
    def sleep(self):
        """Put computer to sleep"""
        self.logger.info("Putting system to sleep...")
        if self.is_windows:
            try:
                import ctypes
                ctypes.windll.PowrProf.SetSuspendState(0, 1, 0)
            except Exception as e:
                self.logger.error(f"Sleep error: {e}")
    
    def lock_screen(self):
        """Lock the computer screen"""
        self.logger.info("Locking screen...")
        if self.is_windows:
            subprocess.run(['rundll32.exe', 'user32.dll,LockWorkStation'], shell=False)
        else:
            subprocess.run(['loginctl', 'lock-session'], shell=False)
    
    # ==================== Volume Control ====================
    
    def volume_up(self, steps=2):
        """Increase volume"""
        try:
            if self.is_windows:
                import pyautogui
                for _ in range(steps):
                    pyautogui.press('volumeup')
            self.logger.info("Volume increased")
        except Exception as e:
            self.logger.error(f"Volume up error: {e}")
    
    def volume_down(self, steps=2):
        """Decrease volume"""
        try:
            if self.is_windows:
                import pyautogui
                for _ in range(steps):
                    pyautogui.press('volumedown')
            self.logger.info("Volume decreased")
        except Exception as e:
            self.logger.error(f"Volume down error: {e}")
    
    def set_volume(self, level):
        """Set volume to specific level (0-100)"""
        try:
            if self.is_windows:
                # Use pyautogui to set volume (press volume up/down to reach target)
                import pyautogui
                
                # Get current volume estimation - start from 50%
                current_volume = 50
                diff = level - current_volume
                
                # Each press is approximately 2% volume change
                steps = abs(diff) // 2
                if diff > 0:
                    for _ in range(steps):
                        pyautogui.press('volumeup')
                elif diff < 0:
                    for _ in range(steps):
                        pyautogui.press('volumedown')
                
                self.logger.info(f"Volume set to approximately {level}% via pyautogui")
            else:
                # For non-Windows, use amixer or osascript
                import subprocess
                try:
                    subprocess.run(['osascript', '-e', f'set volume output volume {level}'], check=True)
                    self.logger.info(f"Volume set to {level}%")
                except:
                    self.logger.warning("Volume control not supported on this platform")
        except Exception as e:
            self.logger.error(f"Set volume error: {e}")
    
    def mute(self):
        """Mute volume"""
        try:
            if self.is_windows:
                import pyautogui
                pyautogui.press('volumemute')
            self.logger.info("Volume muted")
        except Exception as e:
            self.logger.error(f"Mute error: {e}")
    
    # ==================== Brightness Control ====================
    
    def brightness_up(self):
        """Increase brightness"""
        try:
            if self.is_windows:
                import pyautogui
                pyautogui.press('brightnessup')
            self.logger.info("Brightness increased")
        except Exception as e:
            self.logger.error(f"Brightness up error: {e}")
    
    def brightness_down(self):
        """Decrease brightness"""
        try:
            if self.is_windows:
                import pyautogui
                pyautogui.press('brightnessdown')
            self.logger.info("Brightness decreased")
        except Exception as e:
            self.logger.error(f"Brightness down error: {e}")
    
    # ==================== Screenshot ====================
    
    def take_screenshot(self, filename=None):
        """Take a screenshot"""
        try:
            if not filename:
                filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            
            import pyautogui
            screenshot = pyautogui.screenshot()
            screenshot.save(filename)
            self.logger.info(f"Screenshot saved: {filename}")
            return filename
        except Exception as e:
            self.logger.error(f"Screenshot error: {e}")
            return None
    
    # ==================== Application Control ====================
    
    def open_app(self, app_name):
        """Open an application"""
        self.logger.info(f"Opening application: {app_name}")
        
        app_paths = {
            'chrome': 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
            'vscode': 'C:\\Users\\ARYAN POTE\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe',
            'notepad': 'notepad.exe',
            'word': 'C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE',
            'excel': 'C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE',
            'powerpoint': 'C:\\Program Files\\Microsoft Office\\root\\Office16\\POWERPNT.EXE',
            'calculator': 'calc.exe',
            'settings': 'ms-settings:',
            'file explorer': 'explorer.exe',
            'terminal': 'cmd.exe',
            'powershell': 'powershell.exe',
        }
        
        app_key = app_name.lower().strip()
        if app_key in app_paths:
            path = app_paths[app_key]
            try:
                if path.startswith('C:\\') or path.startswith('/'):
                    subprocess.Popen(path)
                else:
                    subprocess.Popen(path, shell=True)
                return True
            except Exception as e:
                self.logger.error(f"Open app error: {e}")
        
        # Try system search
        try:
            subprocess.Popen(f'start {app_name}', shell=True)
            return True
        except Exception as e:
            self.logger.error(f"Search app error: {e}")
            return False
    
    # ==================== Media Control ====================
    
    def media_control(self, action):
        """Control media playback"""
        try:
            import pyautogui
            if action == 'play' or action == 'pause':
                pyautogui.press('playpause')
            elif action == 'next':
                pyautogui.press('nexttrack')
            elif action == 'previous':
                pyautogui.press('prevtrack')
            elif action == 'stop':
                pyautogui.press('stop')
            self.logger.info(f"Media {action} command sent")
        except Exception as e:
            self.logger.error(f"Media control error: {e}")
    
    # ==================== Internet & Web ====================
    
    def internet_search(self, query):
        """Perform internet search"""
        try:
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(url)
            self.logger.info(f"Searching for: {query}")
            return True
        except Exception as e:
            self.logger.error(f"Search error: {e}")
            return False
    
    def send_whatsapp(self, contact_name, message):
        """Send WhatsApp message"""
        try:
            encoded_message = requests.utils.quote(message)
            url = f"https://web.whatsapp.com/send?phone={contact_name}&text={encoded_message}"
            webbrowser.open(url)
            self.logger.info(f"Sending WhatsApp to {contact_name}")
            return True
        except Exception as e:
            self.logger.error(f"WhatsApp error: {e}")
            return False
    
    # ==================== Weather & News ====================
    
    def get_weather(self, location=None):
        """Get weather information"""
        try:
            if location:
                url = f"https://wttr.in/{location}?format=j1"
            else:
                url = "https://wttr.in/?format=j1"
            
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                current = data['current_condition'][0]
                temp = current['temp_C'][0]
                condition = current['weatherDesc'][0]['value']
                humidity = current['humidity'][0]
                
                return f"Currently, it's {temp} degrees Celsius with {condition}. Humidity is {humidity} percent."
            return "Unable to get weather information"
        except Exception as e:
            self.logger.error(f"Weather error: {e}")
            return "Sorry, I couldn't get the weather information"
    
    def get_news(self, category='general'):
        """Get news briefing"""
        try:
            return "Here's your news briefing: Top stories today include technology advances and global events. Would you like me to search for specific news?"
        except Exception as e:
            self.logger.error(f"News error: {e}")
            return "Sorry, I couldn't get the news at the moment"
    
    # ==================== File Operations ====================
    
    def find_file(self, filename, search_path=None):
        """Search for a file in the system"""
        try:
            if not search_path:
                search_path = os.path.expanduser('~')
            
            for root, dirs, files in os.walk(search_path):
                if filename in files:
                    full_path = os.path.join(root, filename)
                    self.logger.info(f"Found file: {full_path}")
                    return full_path
            return None
        except Exception as e:
            self.logger.error(f"File search error: {e}")
            return None
    
    def open_file(self, filepath):
        """Open a file with default application"""
        try:
            if sys.platform == 'win32':
                os.startfile(filepath)
            else:
                subprocess.run(['open', filepath])
            return True
        except Exception as e:
            self.logger.error(f"Open file error: {e}")
            return False
    
    # ==================== Email ====================
    
    def send_email(self, recipient, subject, body):
        """Send an email (using default mail client)"""
        try:
            mailto = f"mailto:{recipient}?subject={subject}&body={body}"
            webbrowser.open(mailto)
            self.logger.info(f"Opening email to {recipient}")
            return True
        except Exception as e:
            self.logger.error(f"Email error: {e}")
            return False
    
    # ==================== Clipboard ====================
    
    def copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        try:
            import pyperclip
            pyperclip.copy(text)
            self.logger.info("Text copied to clipboard")
            return True
        except Exception as e:
            self.logger.error(f"Clipboard error: {e}")
            return False
    
    def paste_from_clipboard(self):
        """Get text from clipboard"""
        try:
            import pyperclip
            return pyperclip.paste()
        except Exception as e:
            self.logger.error(f"Clipboard read error: {e}")
            return None


# ==================== Standalone Functions for karma.py ====================

def open_word():
    """Open Microsoft Word"""
    import subprocess
    import os
    
    # Common Word installation paths
    word_paths = [
        r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
        r"C:\Program Files\Microsoft Office\root\Office15\WINWORD.EXE",
        r"C:\Program Files (x86)\Microsoft Office\root\Office16\WINWORD.EXE",
        r"C:\Program Files (x86)\Microsoft Office\root\Office15\WINWORD.EXE",
    ]
    
    # Try each path
    for path in word_paths:
        if os.path.exists(path):
            try:
                subprocess.Popen([path])
                return True
            except Exception:
                pass
    
    # Fallback: Try to open via Windows
    try:
        subprocess.Popen("start winword", shell=True)
        return True
    except Exception:
        return False
    
    return False


def open_powerpoint():
    """Open Microsoft PowerPoint"""
    import subprocess
    import os
    
    # Common PowerPoint installation paths
    ppt_paths = [
        r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
        r"C:\Program Files\Microsoft Office\root\Office15\POWERPNT.EXE",
        r"C:\Program Files (x86)\Microsoft Office\root\Office16\POWERPNT.EXE",
        r"C:\Program Files (x86)\Microsoft Office\root\Office15\POWERPNT.EXE",
    ]
    
    # Try each path
    for path in ppt_paths:
        if os.path.exists(path):
            try:
                subprocess.Popen([path])
                return True
            except Exception:
                pass
    
    # Fallback: Try to open via Windows
    try:
        subprocess.Popen("start powerpnt", shell=True)
        return True
    except Exception:
        return False
    
    return False


def open_vscode():
    """Open Visual Studio Code"""
    import subprocess
    import os
    
    # Common VS Code installation paths
    vscode_paths = [
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe"),
        r"C:\Program Files\Microsoft VS Code\Code.exe",
        r"C:\Program Files (x86)\Microsoft VS Code\Code.exe",
    ]
    
    # Try each path
    for path in vscode_paths:
        if os.path.exists(path):
            try:
                subprocess.Popen([path])
                return True
            except Exception:
                pass
    
    # Fallback: Try to open via PATH
    try:
        subprocess.Popen("code")
        return True
    except Exception:
        pass
    
    # Final fallback: Try Windows start command
    try:
        subprocess.Popen("start code", shell=True)
        return True
    except Exception:
        return False
    
    return False


def open_excel():
    """Open Microsoft Excel"""
    import subprocess
    import os
    
    # Common Excel installation paths
    excel_paths = [
        r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
        r"C:\Program Files\Microsoft Office\root\Office15\EXCEL.EXE",
        r"C:\Program Files (x86)\Microsoft Office\root\Office16\EXCEL.EXE",
        r"C:\Program Files (x86)\Microsoft Office\root\Office15\EXCEL.EXE",
    ]
    
    # Try each path
    for path in excel_paths:
        if os.path.exists(path):
            try:
                subprocess.Popen([path])
                return True
            except Exception:
                pass
    
    # Fallback: Try to open via Windows
    try:
        subprocess.Popen("start excel", shell=True)
        return True
    except Exception:
        return False
    
    return False


def restart_pc(delay=1):
    """Restart the PC"""
    import subprocess
    try:
        subprocess.run(['shutdown', '/r', '/t', str(delay)], shell=False, check=False)
        return True
    except Exception:
        # Fallback for Windows
        try:
            subprocess.run(f"shutdown /r /t {delay}", shell=True, check=False)
            return True
        except Exception:
            return False


def shutdown_pc(delay=1):
    """Shutdown the PC"""
    import subprocess
    try:
        subprocess.run(['shutdown', '/s', '/t', str(delay)], shell=False, check=False)
        return True
    except Exception:
        # Fallback for Windows
        try:
            subprocess.run(f"shutdown /s /t {delay}", shell=True, check=False)
            return True
        except Exception:
            return False


def sleep_pc():
    """Put the PC to sleep"""
    import subprocess
    try:
        subprocess.run(['rundll32.exe', 'powrprof.dll,SetSuspendState', '0,1,0'], 
                       shell=False, check=False)
        return True
    except Exception:
        # Fallback
        try:
            subprocess.run("rundll32.exe powrprof.dll,SetSuspendState 0,1,0", 
                          shell=True, check=False)
            return True
        except Exception:
            return False


def lock_pc():
    """Lock the PC"""
    import subprocess
    try:
        subprocess.run(['rundll32.exe', 'user32.dll,LockWorkStation'], 
                       shell=False, check=False)
        return True
    except Exception:
        # Fallback
        try:
            subprocess.run("rundll32.exe user32.dll,LockWorkStation", 
                          shell=True, check=False)
            return True
        except Exception:
            return False


def open_notepad():
    """Open Notepad"""
    import subprocess
    try:
        subprocess.Popen("notepad.exe")
        return True
    except Exception:
        try:
            subprocess.Popen("start notepad", shell=True)
            return True
        except Exception:
            return False


def open_calculator():
    """Open Calculator"""
    import subprocess
    try:
        subprocess.Popen("calc.exe")
        return True
    except Exception:
        try:
            subprocess.Popen("start calc", shell=True)
            return True
        except Exception:
            return False


def open_file_explorer():
    """Open File Explorer"""
    import subprocess
    try:
        subprocess.Popen("explorer.exe")
        return True
    except Exception:
        return False


def open_command_prompt():
    """Open Command Prompt"""
    import subprocess
    try:
        subprocess.Popen("cmd.exe")
        return True
    except Exception:
        try:
            subprocess.Popen("start cmd", shell=True)
            return True
        except Exception:
            return False


def open_task_manager():
    """Open Task Manager"""
    import subprocess
    try:
        subprocess.Popen("taskmgr.exe")
        return True
    except Exception:
        try:
            subprocess.Popen("start taskmgr", shell=True)
            return True
        except Exception:
            return False


def open_control_panel():
    """Open Control Panel"""
    import subprocess
    try:
        subprocess.Popen("control.exe")
        return True
    except Exception:
        try:
            subprocess.Popen("start control", shell=True)
            return True
        except Exception:
            return False


def open_settings():
    """Open Windows Settings"""
    import subprocess
    try:
        subprocess.Popen("ms-settings:")
        return True
    except Exception:
        return False
