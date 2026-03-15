"""
KARMA AI - Voice Assistant
Main Entry Point - Production Ready Version
"""

import speech_recognition as sr
import webbrowser
import pyttsx3
import sys
import os
import subprocess
import pyautogui
import requests
from datetime import datetime


karma_ai_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'karma_ai')
if karma_ai_path not in sys.path:
    sys.path.insert(0, karma_ai_path)

from karma_ai.musicLibrary import MusicLibrary

from karma_ai.automation import (
    open_word, open_powerpoint, open_vscode, open_excel,
    restart_pc, shutdown_pc, sleep_pc, lock_pc,
    open_notepad, open_calculator, open_file_explorer,
    open_command_prompt, open_task_manager, open_control_panel
)

music_lib = MusicLibrary()
music = music_lib.music  


recognizer = sr.Recognizer()

try:
    engine = pyttsx3.init()

    engine.setProperty('rate', 175)  
    engine.setProperty('volume', 1.0)  
    voices = engine.getProperty('voices')
    for voice in voices:
        if 'english' in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break
except Exception as e:
    print(f"TTS init error: {e}")
    engine = None

def speak(text):
    """Speak text with error handling"""
    if not engine:
        print(f"Cannot speak: {text}")
        return
    try:
        engine.say(text)
        engine.runAndWait()
    except RuntimeError:
        try:
            import time
            time.sleep(0.1)
            engine.runAndWait()
        except:
            pass
    except Exception as e:
        print(f"Speak error: {e}")

def generate_image(prompt):
    """
    Generate an AI image using DALL-E API and save to Desktop/Karma_Images/
    """
    try:
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        karma_images_folder = os.path.join(desktop_path, "Karma_Images")
        
        if not os.path.exists(karma_images_folder):
            os.makedirs(karma_images_folder)
            print(f"Created folder: {karma_images_folder}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"image_{timestamp}.png"
        filepath = os.path.join(karma_images_folder, filename)
        
       
        try:
            from openai import OpenAI
            client = OpenAI()  
            
            
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            
            image_url = response.data[0].url
            
            img_response = requests.get(image_url)
            if img_response.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(img_response.content)
                print(f"Image saved to: {filepath}")
                return True, filepath
            else:
                print(f"Failed to download image: {img_response.status_code}")
                return False, None
                
        except ImportError:
            print("OpenAI not available, trying HuggingFace...")
            

            from huggingface_hub import hf_hub_download

            print("Image generation requires OpenAI API key or local Stable Diffusion")
            print("Please install openai and set OPENAI_API_KEY environment variable")
            return False, None
            
    except Exception as e:
        print(f"Image generation error: {e}")
        return False, None

def voice_typing():
    speak("Voice typing mode activated. Say stop typing to exit.")
    
    r = sr.Recognizer()
    
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=1)
        
        while True:
            try:
                print("Typing mode listening...")
                audio = r.listen(source)
                text = r.recognize_google(audio, language="en-IN")
                
                print("Typing:", text)
                
                if "stop typing" in text.lower():
                    speak("Exiting voice typing mode")
                    break
                
                pyautogui.write(text + " ")
                
            except sr.UnknownValueError:
                print("Didn't catch that...")
            except sr.RequestError:
                speak("Network error")
                break
            except Exception as e:
                print("Typing Error:", e)
                break


def typing_mode():
    """
    Typing Mode - Opens Notepad and continuously listens to voice input,
    converting speech to text and typing it in Notepad.
    
    Activated by: "start typing" or "start writing mode"
    Deactivated by: "stop typing" or "stop writing mode"
    """

    speak("Writing mode is activated.")
 
    try:
        os.system("start notepad")
        import time
        time.sleep(2)
    except Exception as e:
        print(f"Error opening Notepad: {e}")
        try:
            subprocess.Popen(["notepad.exe"])
            time.sleep(2)
        except:
            pass
    
    pyautogui.PAUSE = 0.05  
    
    r = sr.Recognizer()
    
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=1)
        
        while True:
            try:
                print("Typing mode listening...")
                audio = r.listen(source, timeout=5, phrase_time_limit=10)
                text = r.recognize_google(audio, language="en-IN")
                
                print("Recognized:", text)

                if "stop typing" in text.lower() or "stop writing mode" in text.lower():
                    speak("Karma writing mode is off.")
                    break
                
                if text:
                    import time
                    time.sleep(0.2)
                    pyautogui.write(str(text), interval=0.05)
                    pyautogui.press("space")
                
            except sr.UnknownValueError:
                speak("I didn't understand. Please repeat.")
            except sr.RequestError:
                speak("Network error. Please check your connection.")
                break
            except sr.WaitTimeoutError:
                continue
            except Exception as e:
                print("Typing Error:", e)
                break



def processCommand(c):

    c = c.lower()
    response = None

    if "open google" in c:
        webbrowser.open("https://www.google.com")
        response = "Opening Google"

    elif "open facebook" in c:
        webbrowser.open("https://www.facebook.com")
        response = "Opening Facebook"

    elif "open youtube" in c:
        webbrowser.open("https://www.youtube.com")
        response = "Opening YouTube"

    elif "open linkedin" in c:
        webbrowser.open("https://www.linkedin.com")
        response = "Opening LinkedIn"

    elif "start typing" in c or "start writing mode" in c or "voice typing" in c:
        typing_mode()
        return

    elif "open github" in c:
        webbrowser.open("https://www.github.com")
        response = "Opening GitHub"

    elif "open instagram" in c:
        webbrowser.open("https://www.instagram.com")
        response = "Opening Instagram"

    elif "open twitter" in c:
        webbrowser.open("https://www.twitter.com")
        response = "Opening Twitter"

    elif "open whatsapp" in c:
        try:
            os.system("start whatsapp:")
            response = "Opening WhatsApp app"
        except:
            webbrowser.open("https://web.whatsapp.com")
            response = "Opening WhatsApp Web"


    elif "open stackoverflow" in c:
        webbrowser.open("https://stackoverflow.com")
        response = "Opening Stack Overflow"

    elif "open firefox" in c:
        webbrowser.open("https://www.mozilla.org/en-US/firefox/new/")
        response = "Opening Firefox"

    elif "open chrome" in c:
        webbrowser.open("https://www.google.com/chrome/")
        response = "Opening Chrome"

    elif "open edge" in c:
        webbrowser.open("https://www.microsoft.com/en-US/edge")
        response = "Opening Edge"

    elif "open spotify" in c:
        try:
            os.system("start spotify:")
            response = "Opening Spotify app"
        except:
            webbrowser.open("https://open.spotify.com")
            response = "Opening Spotify in browser"


    elif "open netflix" in c:
        webbrowser.open("https://www.netflix.com")
        response = "Opening Netflix"

    elif "open prime video" in c:
        webbrowser.open("https://www.primevideo.com")
        response = "Opening Prime Video"

    elif "call phone" in c or "open phone link" in c or "make phone call" in c:
        speak("Please enter the phone number.")
        number = input("Enter phone number: ")
        webbrowser.open(f"tel:{number}")
        response = f"Calling {number}"

    elif "open open ai" in c or "open chatgpt" in c or "open gpt" in c:
        speak("Opening ChatGPT")
        os.system("start chatgpt")

    elif "open gmail" in c:
        webbrowser.open("https://mail.google.com")
        response = "Opening Gmail"

    elif "open youtube music" in c:
        webbrowser.open("https://music.youtube.com")
        response = "Opening YouTube Music"

    elif "open vs code" in c or "open vscode" in c:
        speak("Opening Visual Studio Code")
        os.system("code")
        
    elif "open opera" in c:
        webbrowser.open("https://www.opera.com")
        response = "Opening Opera"

    elif "open canva" in c:
        webbrowser.open("https://www.canva.com")
        response = "Opening Canva"

    elif "open flipkart" in c:
        webbrowser.open("https://www.flipkart.com")
        response = "Opening Flipkart"

    elif "open amazon" in c:
        webbrowser.open("https://www.amazon.in")
        response = "Opening Amazon"

    elif "open notes" in c:
        webbrowser.open("https://keep.google.com")
        response = "Opening Google Keep"

    elif "open maps" in c:
        webbrowser.open("https://www.google.com/maps")
        response = "Opening Google Maps"

    elif "open news" in c:
        webbrowser.open("https://news.google.com")
        response = "Opening Google News"

    elif "open calendar" in c:
        webbrowser.open("https://calendar.google.com")
        response = "Opening Google Calendar"

    elif "open gemini ai" in c:
        webbrowser.open("https://gemini.google.com")
        response = "Opening Gemini AI"

    elif "open drive" in c:
        webbrowser.open("https://drive.google.com")
        response = "Opening Google Drive"

    elif "open translate" in c:
        webbrowser.open("https://translate.google.com")
        response = "Opening Google Translate"

    elif "open docs" in c:
        webbrowser.open("https://docs.google.com")
        response = "Opening Google Docs"

    elif "open camera" in c:
        speak("Opening your PC camera")
        os.system("start microsoft.windows.camera:")
        response = "Opening camera"

    elif "open calculator" in c:
        open_calculator()
        response = "Opening calculator"

    elif "open weather" in c:
        webbrowser.open("https://www.weather.com")
        response = "Opening weather"

    elif "open dictionary" in c:
        webbrowser.open("https://www.dictionary.com")
        response = "Opening dictionary"

    elif "open hotstar" in c:
        webbrowser.open("https://www.hotstar.com")
        response = "Opening Hotstar"

    elif "open jio cinema" in c:
        webbrowser.open("https://www.jiocinema.com")
        response = "Opening Jio Cinema"

    elif "open jio tv" in c:
        webbrowser.open("https://www.jiotv.com")
        response = "Opening Jio TV"

    elif "open jio" in c:
        webbrowser.open("https://www.jio.com")
        response = "Opening Jio"

    elif "open meet" in c:
        webbrowser.open("https://meet.google.com")
        response = "Opening Google Meet"

    elif "open zoom" in c:
        webbrowser.open("https://zoom.us")
        response = "Opening Zoom"

    elif "open cricbuzz" in c:
        webbrowser.open("https://www.cricbuzz.com")
        response = "Opening Cricbuzz"

    elif "open classroom" in c:
        webbrowser.open("https://classroom.google.com")
        response = "Opening Google Classroom"

    elif "open google photos" in c  or "open photos" in c:
        os.system('start chrome --app="https://photos.google.com"')
        response = "Opening Google Photos"

    elif "shutdown pc" in c or "shutdown computer" in c:
        speak("Shutting down the PC")
        shutdown_pc()
        response = "Shutting down"

    elif "restart pc" in c or "restart computer" in c or "reboot pc" in c:
        speak("Restarting the computer")
        restart_pc()
        response = "Restarting"
        
    elif "sleep pc" in c or "sleep computer" in c or "put to sleep" in c:
        speak("Putting the PC to sleep")
        sleep_pc()
        response = "Sleeping"
        
    elif "lock pc" in c or "lock computer" in c or "lock screen" in c:
        speak("Locking the PC")
        lock_pc()
        response = "Locking"

    elif "hibernate pc" in c or "hibernate computer" in c:
        speak("Hibernating the PC")
        shutdown_pc()  
        response = "Hibernating"

    elif "open command prompt" in c or "open cmd" in c:
        open_command_prompt()
        response = "Opening command prompt"

    elif "open task manager" in c:
        open_task_manager()
        response = "Opening task manager"

    elif "open control panel" in c:
        open_control_panel()
        response = "Opening control panel"

    elif "open file explorer" in c or "open explorer" in c:
        open_file_explorer()
        response = "Opening file explorer"

    elif "open notepad" in c:
        open_notepad()
        response = "Opening notepad"

    elif "open ms word" in c or "open microsoft word" in c or "open word" in c:
        open_word()
        response = "Opening Microsoft Word"

    elif "open ms excel" in c or "open microsoft excel" in c or "open excel" in c:
        open_excel()
        response = "Opening Microsoft Excel"

    elif "open ms powerpoint" in c or "open microsoft powerpoint" in c or "open powerpoint" in c:
        open_powerpoint()
        response = "Opening Microsoft PowerPoint"

    elif "open python" in c:
        # Try to open Python
        try:
            import subprocess
            subprocess.Popen("python")
            response = "Opening Python"
        except Exception:
            speak("Could not open Python")

    elif "open microsoft edge" in c or "open edge" in c:
        try:
            import subprocess
            subprocess.Popen("msedge")
            response = "Opening Microsoft Edge"
        except Exception:
            webbrowser.open("https://www.microsoft.com/en-us/edge")
            response = "Opening Microsoft Edge"

    elif "open maps" in c or "open map" in c or "google map" in c or "google maps" in c:
        webbrowser.open("https://www.google.com/maps")
        response = "Opening Google Maps"

    elif c.startswith("play"):
        song = c.split(" ", 1)[1] if len(c.split(" ", 1)) > 1 else ""
        
        if song:
            link = music.get(song)
            if link:
                speak(f"Playing {song}")
                webbrowser.open(link)
            else:
                found = False
                for song_name, url in music.items():
                    if song in song_name:
                        speak(f"Playing {song_name}")
                        webbrowser.open(url)
                        found = True
                        break
                if not found:
                    import urllib.parse
                    search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(song + ' song')}"
                    webbrowser.open(search_url)
                    speak(f"Searching for {song}")
    
    elif "play popular" in c or "popular music" in c:
        speak("Playing popular music")
        webbrowser.open("https://www.youtube.com/results?search_query=top+english+songs+2024")
        
    elif "play bollywood" in c or "hindi songs" in c or "bollywood music" in c:
        speak("Playing Bollywood music")
        webbrowser.open("https://www.youtube.com/results?search_query=top+bollywood+songs+2024")
        
    elif "play relaxing" in c or "chill music" in c or "lofi" in c:
        speak("Playing relaxing music")
        webbrowser.open("https://www.youtube.com/watch?v=jfKfPfyJRdk")
        
    elif "play classical" in c or "classical music" in c:
        speak("Playing classical music")
        webbrowser.open("https://www.youtube.com/watch?v=hZ9p78XS2N8")
        
    elif "play workout" in c or "gym music" in c or "pump up" in c:
        speak("Playing workout music")
        webbrowser.open("https://www.youtube.com/watch?v=ml6cT4AZdqI")
        
    elif "play devotional" in c or "bhajans" in c or "aarti" in c:
        speak("Playing devotional music")
        webbrowser.open("https://www.youtube.com/results?search_query=hindi+devotional+songs")
        
    elif "play punjabi" in c:
        speak("Playing Punjabi music")
        webbrowser.open("https://www.youtube.com/results?search_query=top+punjabi+songs")
        
    elif "play sad" in c or "heartbreak" in c:
        speak("Playing sad songs")
        webbrowser.open("https://www.youtube.com/results?search_query=sad+songs+hindi+english")
        
    elif "play party" in c or "dj" in c:
        speak("Playing party music")
        webbrowser.open("https://www.youtube.com/results?search_query=party+songs+hindi+english")
        
    elif "list songs" in c or "all songs" in c or "show songs" in c:
        speak("Opening music library. Here are some popular songs you can play:")
        all_songs = list(music.keys())[:20]
        songs_list = ", ".join(all_songs)
        speak(songs_list)
        webbrowser.open("https://www.youtube.com/watch?v=JGwWNGJdvx8")
        response = "Listed available songs"

    elif "open music" in c or "open all music" in c or "play all music" in c:
        speak("Opening YouTube music for you")
        webbrowser.open("https://music.youtube.com")
        response = "Opening music"

    elif "generate image" in c or "create image" in c or "make image" in c:
        prompt = ""
        if "generate image" in c:
            prompt = c.split("generate image", 1)[1].strip()
        elif "create image" in c:
            prompt = c.split("create image", 1)[1].strip()
        elif "make image" in c:
            prompt = c.split("make image", 1)[1].strip()
        
        if prompt:
            speak("Generating your image, please wait.")
            success, filepath = generate_image(prompt)
            if success:
                speak("Your image has been generated and saved to the Karma Images folder.")
            else:
                speak("Sorry, I couldn't generate the image.")
        else:
            speak("Please specify what image you want to generate.")

    else:
        speak("I don't understand that command. Please speak clearly.")
        return

    if response:
        speak(response)


if __name__ == "__main__":
    speak("Karma AI is now fully activated and operating at maximum potential. 🚀All systems are online, intelligence modules are loaded, and I’m ready to assist you with anything—from coding and automation to research, creativity, productivity, and problem-solving.")
   
    r = sr.Recognizer()

    r.energy_threshold = 200  
    r.pause_threshold = 0.5  
    r.phrase_threshold = 0.2  
    r.dynamic_energy_threshold = True

    mic = sr.Microphone()
    
    with mic as source:
        print("Calibrating Karma...")
        r.adjust_for_ambient_noise(source, duration=2)
        print(f"Karma ready - Energy threshold: {r.energy_threshold}")

    while True:
        print("Karma is listening...")

        try:
            print("Listening for audio...")
            with mic as source:
                audio = r.listen(source, timeout=5, phrase_time_limit=8)
            
            print("Recognizing...")
            command = r.recognize_google(audio, language="en-IN")
            print("Heard:", command)

            if "karma" in command.lower():
                cmd_lower = command.lower()
               
                if "karma" in cmd_lower:
                    idx = cmd_lower.find("karma") + len("karma")
                    actual_command = cmd_lower[idx:].strip()
                    
                    if actual_command:
                        processCommand(actual_command)
                    else:
                        speak("Yes")
                else:
                    speak("Yes")

            elif "stop" in command.lower() or "exit" in command.lower() or "quit" in command.lower():
                speak("Goodbye! Have a great day!")
                break

            else:
                processCommand(command)

        except sr.WaitTimeoutError:
            print("Silence detected")

        except sr.UnknownValueError:
            speak("I didn't understand what you said. Please speak clearly.")

        except sr.RequestError:
            print("Check your internet connection")

        except Exception as e:
            print("Error:", e)