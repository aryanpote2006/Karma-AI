"""
Enhanced GUI Module for KARMA AI
CustomTkinter-based JARVIS-style futuristic interface

Features:
- Neon blue JARVIS theme
- Animated listening indicator
- System status panel (CPU, RAM, Battery)
- Digital clock with date
- Mic animation
- Advanced status display
"""

import customtkinter as ctk
from tkinter import scrolledtext
import threading
import psutil
import time
from datetime import datetime
import logging


class EnhancedGUI:
    """
    Enhanced GUI Dashboard for KARMA AI
    Features JARVIS-style futuristic interface with:
    - Neon blue color scheme
    - Animated indicators
    - System monitoring
    - Voice waveform visualization
    """
    
    def __init__(self, voice_engine, command_processor, ai_brain, memory, logger=None):
        """Initialize Enhanced GUI components"""
        self.logger = logger or logging.getLogger('KARMA-GUI-Enhanced')
        
        # Core components
        self.voice_engine = voice_engine
        self.command_processor = command_processor
        self.ai_brain = ai_brain
        self.memory = memory
        
        # State
        self.is_listening = False
        self.is_speaking = False
        self.is_thinking = False
        
        # Configure CustomTkinter appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Colors - JARVIS neon blue theme
        self.colors = {
            'bg_dark': '#0a0a12',
            'bg_medium': '#12121f',
            'bg_light': '#1a1a2e',
            'neon_blue': '#00d4ff',
            'neon_blue_dim': '#007a99',
            'neon_cyan': '#00fff7',
            'text_primary': '#ffffff',
            'text_secondary': '#8892b0',
            'success': '#00ff88',
            'warning': '#ffaa00',
            'error': '#ff4444',
            'accent': '#6366f1'
        }
        
        # Setup GUI
        self.root = None
        self._setup_gui()
        
        # Start background threads
        self.running = True
        self.system_thread = threading.Thread(target=self._system_monitor, daemon=True)
        self.system_thread.start()
        
        self.logger.info("Enhanced GUI initialized")
    
    def _setup_gui(self):
        """Setup the enhanced GUI interface"""
        # Main window
        self.root = ctk.CTk()
        self.root.title("KARMA AI - Personal Assistant")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        self.root.configure(fg_color=self.colors['bg_dark'])
        
        # Configure grid
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
        # Create sections
        self._create_header()
        self._create_sidebar()
        self._create_main_panel()
        self._create_status_bar()
    
    def _create_header(self):
        """Create header with logo and clock"""
        header_frame = ctk.CTkFrame(self.root, fg_color=self.colors['bg_medium'], height=80)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
        header_frame.grid_propagate(False)
        
        # Logo section
        logo_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        logo_frame.pack(side="left", padx=30, pady=15)
        
        # KARMA logo with glow effect (using label)
        self.logo_label = ctk.CTkLabel(
            logo_frame,
            text="◈ KARMA",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=self.colors['neon_blue']
        )
        self.logo_label.pack()
        
        # Subtitle
        self.subtitle_label = ctk.CTkLabel(
            logo_frame,
            text="ADVANCED AI ASSISTANT",
            font=ctk.CTkFont(size=10, weight="normal"),
            text_color=self.colors['text_secondary']
        )
        self.subtitle_label.pack()
        
        # Right side - Clock and status
        right_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        right_frame.pack(side="right", padx=30, pady=15)
        
        # Digital clock
        self.clock_label = ctk.CTkLabel(
            right_frame,
            text="00:00:00",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color=self.colors['neon_cyan']
        )
        self.clock_label.pack()
        
        # Date
        self.date_label = ctk.CTkLabel(
            right_frame,
            text="Loading...",
            font=ctk.CTkFont(size=12),
            text_color=self.colors['text_secondary']
        )
        self.date_label.pack()
        
        # Update time
        self._update_time()
    
    def _create_sidebar(self):
        """Create sidebar with controls"""
        sidebar = ctk.CTkFrame(self.root, fg_color=self.colors['bg_medium'], width=200)
        sidebar.grid(row=1, column=0, sticky="ns", padx=0, pady=0)
        sidebar.grid_propagate(False)
        
        # Status indicators section
        status_section = ctk.CTkLabel(
            sidebar,
            text="STATUS",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors['neon_blue']
        )
        status_section.pack(pady=(20, 10), padx=20)
        
        # Listening indicator (animated)
        self.listening_frame = ctk.CTkFrame(sidebar, fg_color=self.colors['bg_light'], height=50)
        self.listening_frame.pack(fill="x", padx=15, pady=5)
        
        self.listening_canvas = ctk.CTkCanvas(
            self.listening_frame,
            width=30,
            height=30,
            bg=self.colors['bg_light'],
            highlightthickness=0
        )
        self.listening_canvas.pack(side="left", padx=10, pady=10)
        
        # Draw listening circle
        self.listening_circle = self.listening_canvas.create_oval(
            5, 5, 25, 25,
            fill=self.colors['bg_light'],
            outline=self.colors['neon_blue'],
            width=2
        )
        
        self.listening_label = ctk.CTkLabel(
            self.listening_frame,
            text="IDLE",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=self.colors['text_secondary']
        )
        self.listening_label.pack(side="left", padx=5)
        
        # Thinking indicator
        self.thinking_frame = ctk.CTkFrame(sidebar, fg_color=self.colors['bg_light'], height=50)
        self.thinking_frame.pack(fill="x", padx=15, pady=5)
        
        self.thinking_canvas = ctk.CTkCanvas(
            self.thinking_frame,
            width=30,
            height=30,
            bg=self.colors['bg_light'],
            highlightthickness=0
        )
        self.thinking_canvas.pack(side="left", padx=10, pady=10)
        
        self.thinking_circle = self.thinking_canvas.create_oval(
            5, 5, 25, 25,
            fill=self.colors['bg_light'],
            outline=self.colors['warning'],
            width=2
        )
        
        self.thinking_label = ctk.CTkLabel(
            self.thinking_frame,
            text="READY",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=self.colors['text_secondary']
        )
        self.thinking_label.pack(side="left", padx=5)
        
        # Speaking indicator
        self.speaking_frame = ctk.CTkFrame(sidebar, fg_color=self.colors['bg_light'], height=50)
        self.speaking_frame.pack(fill="x", padx=15, pady=5)
        
        self.speaking_canvas = ctk.CTkCanvas(
            self.speaking_frame,
            width=30,
            height=30,
            bg=self.colors['bg_light'],
            highlightthickness=0
        )
        self.speaking_canvas.pack(side="left", padx=10, pady=10)
        
        self.speaking_circle = self.speaking_canvas.create_oval(
            5, 5, 25, 25,
            fill=self.colors['bg_light'],
            outline=self.colors['success'],
            width=2
        )
        
        self.speaking_label = ctk.CTkLabel(
            self.speaking_frame,
            text="READY",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=self.colors['text_secondary']
        )
        self.speaking_label.pack(side="left", padx=5)
        
        # Separator
        ctk.CTkLabel(sidebar, text="", height=20).pack()
        
        # System Status section
        sys_section = ctk.CTkLabel(
            sidebar,
            text="SYSTEM",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors['neon_blue']
        )
        sys_section.pack(pady=(10, 10), padx=20)
        
        # CPU usage
        cpu_frame = ctk.CTkFrame(sidebar, fg_color=self.colors['bg_light'])
        cpu_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(cpu_frame, text="CPU", font=ctk.CTkFont(size=10), text_color=self.colors['text_secondary']).pack(anchor="w", padx=10, pady=(5, 0))
        
        self.cpu_progress = ctk.CTkProgressBar(cpu_frame, height=8, progress_color=self.colors['neon_blue'])
        self.cpu_progress.pack(fill="x", padx=10, pady=(0, 5))
        self.cpu_progress.set(0.5)
        
        self.cpu_label = ctk.CTkLabel(cpu_frame, text="50%", font=ctk.CTkFont(size=10), text_color=self.colors['text_primary'])
        self.cpu_label.pack(anchor="e", padx=10, pady=(0, 5))
        
        # RAM usage
        ram_frame = ctk.CTkFrame(sidebar, fg_color=self.colors['bg_light'])
        ram_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(ram_frame, text="RAM", font=ctk.CTkFont(size=10), text_color=self.colors['text_secondary']).pack(anchor="w", padx=10, pady=(5, 0))
        
        self.ram_progress = ctk.CTkProgressBar(ram_frame, height=8, progress_color=self.colors['accent'])
        self.ram_progress.pack(fill="x", padx=10, pady=(0, 5))
        self.ram_progress.set(0.5)
        
        self.ram_label = ctk.CTkLabel(ram_frame, text="50%", font=ctk.CTkFont(size=10), text_color=self.colors['text_primary'])
        self.ram_label.pack(anchor="e", padx=10, pady=(0, 5))
        
        # Battery status
        battery_frame = ctk.CTkFrame(sidebar, fg_color=self.colors['bg_light'])
        battery_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(battery_frame, text="BATTERY", font=ctk.CTkFont(size=10), text_color=self.colors['text_secondary']).pack(anchor="w", padx=10, pady=(5, 0))
        
        self.battery_progress = ctk.CTkProgressBar(battery_frame, height=8, progress_color=self.colors['success'])
        self.battery_progress.pack(fill="x", padx=10, pady=(0, 5))
        self.battery_progress.set(0.8)
        
        self.battery_label = ctk.CTkLabel(battery_frame, text="80%", font=ctk.CTkFont(size=10), text_color=self.colors['text_primary'])
        self.battery_label.pack(anchor="e", padx=10, pady=(0, 5))
        
        # Control buttons
        ctk.CTkLabel(sidebar, text="", height=20).pack()
        
        btn_section = ctk.CTkLabel(
            sidebar,
            text="CONTROLS",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors['neon_blue']
        )
        btn_section.pack(pady=(10, 10), padx=20)
        
        # Listen button
        self.listen_btn = ctk.CTkButton(
            sidebar,
            text="🎤 Listen",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.colors['neon_blue_dim'],
            hover_color=self.colors['neon_blue'],
            text_color=self.colors['text_primary'],
            command=self._start_listening,
            height=40
        )
        self.listen_btn.pack(fill="x", padx=15, pady=5)
        
        # Test voice button
        self.test_btn = ctk.CTkButton(
            sidebar,
            text="🔊 Test Voice",
            font=ctk.CTkFont(size=14),
            fg_color=self.colors['bg_light'],
            hover_color=self.colors['accent'],
            text_color=self.colors['text_primary'],
            command=self._test_voice,
            height=35
        )
        self.test_btn.pack(fill="x", padx=15, pady=5)
        
        # Settings button
        self.settings_btn = ctk.CTkButton(
            sidebar,
            text="⚙ Settings",
            font=ctk.CTkFont(size=14),
            fg_color=self.colors['bg_light'],
            hover_color=self.colors['accent'],
            text_color=self.colors['text_primary'],
            command=self._show_settings,
            height=35
        )
        self.settings_btn.pack(fill="x", padx=15, pady=5)
    
    def _create_main_panel(self):
        """Create main conversation panel"""
        main_frame = ctk.CTkFrame(self.root, fg_color=self.colors['bg_dark'])
        main_frame.grid(row=1, column=1, sticky="nsew", padx=20, pady=20)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title = ctk.CTkLabel(
            main_frame,
            text="◈ CONVERSATION",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['neon_blue']
        )
        title.grid(row=0, column=0, sticky="w", padx=20, pady=(15, 5))
        
        # Chat display
        self.chat_text = scrolledtext.ScrolledText(
            main_frame,
            font=("Consolas", 12),
            bg=self.colors['bg_medium'],
            fg=self.colors['text_primary'],
            wrap="word",
            padx=15,
            pady=15,
            relief="flat",
            bd=0
        )
        self.chat_text.grid(row=1, column=0, sticky="nsew", padx=15, pady=10)
        
        # Configure text tags
        self.chat_text.tag_config('user', foreground=self.colors['neon_blue'])
        self.chat_text.tag_config('ai', foreground=self.colors['success'])
        self.chat_text.tag_config('system', foreground=self.colors['warning'])
        self.chat_text.tag_config('error', foreground=self.colors['error'])
        
        # Input area
        input_frame = ctk.CTkFrame(main_frame, fg_color=self.colors['bg_medium'], height=60)
        input_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 15))
        
        self.command_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Type your command here...",
            font=ctk.CTkFont(size=14),
            fg_color=self.colors['bg_light'],
            border_color=self.colors['neon_blue_dim'],
            text_color=self.colors['text_primary'],
            placeholder_text_color=self.colors['text_secondary'],
            height=40
        )
        self.command_entry.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)
        self.command_entry.bind('<Return>', self._on_command_submit)
        
        # Send button
        send_btn = ctk.CTkButton(
            input_frame,
            text="SEND",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=self.colors['neon_blue'],
            hover_color=self.colors['neon_cyan'],
            text_color=self.colors['bg_dark'],
            command=self._on_command_submit,
            width=80,
            height=40
        )
        send_btn.pack(side="right", padx=(5, 10), pady=10)
    
    def _create_status_bar(self):
        """Create bottom status bar"""
        status_bar = ctk.CTkFrame(self.root, fg_color=self.colors['bg_medium'], height=30)
        status_bar.grid(row=2, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
        status_bar.grid_propagate(False)
        
        # Connection status
        self.connection_label = ctk.CTkLabel(
            status_bar,
            text="● ONLINE",
            font=ctk.CTkFont(size=10),
            text_color=self.colors['success']
        )
        self.connection_label.pack(side="left", padx=20)
        
        # AI status
        self.ai_status_label = ctk.CTkLabel(
            status_bar,
            text="AI: Gemini Ready",
            font=ctk.CTkFont(size=10),
            text_color=self.colors['text_secondary']
        )
        self.ai_status_label.pack(side="left", padx=20)
        
        # Version
        version_label = ctk.CTkLabel(
            status_bar,
            text="v2.0 | KARMA AI",
            font=ctk.CTkFont(size=10),
            text_color=self.colors['text_secondary']
        )
        version_label.pack(side="right", padx=20)
    
    def _update_time(self):
        """Update clock display"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.clock_label.configure(text=current_time)
        
        current_date = datetime.now().strftime("%A, %B %d, %Y")
        self.date_label.configure(text=current_date)
        
        # Schedule next update
        self.root.after(1000, self._update_time)
    
    def _system_monitor(self):
        """Monitor system resources"""
        while self.running:
            try:
                # CPU usage
                cpu = psutil.cpu_percent() / 100.0
                self.cpu_progress.set(cpu)
                self.cpu_label.configure(text=f"{int(cpu*100)}%")
                
                # RAM usage
                ram = psutil.virtual_memory().percent / 100.0
                self.ram_progress.set(ram)
                self.ram_label.configure(text=f"{int(ram*100)}%")
                
                # Battery (if available)
                try:
                    battery = psutil.sensor_battery()
                    if battery:
                        self.battery_progress.set(battery.percent / 100.0)
                        self.battery_label.configure(text=f"{battery.percent}%")
                except:
                    pass
                
            except Exception as e:
                self.logger.error(f"System monitor error: {e}")
            
            time.sleep(2)
    
    def _animate_listening(self):
        """Animate listening indicator"""
        if not self.is_listening:
            return
        
        # Pulse animation
        colors = [self.colors['neon_blue'], self.colors['neon_cyan']]
        current_color = self.listening_canvas.itemcget(self.listening_circle, 'outline')
        new_color = colors[0] if current_color != colors[0] else colors[1]
        
        self.listening_canvas.itemconfig(self.listening_circle, outline=new_color)
        
        # Schedule next frame
        if self.is_listening:
            self.root.after(500, self._animate_listening)
    
    def _on_command_submit(self, event=None):
        """Handle command submission"""
        command = self.command_entry.get().strip()
        if command:
            self._add_message('user', f"You: {command}")
            self.command_entry.delete(0, "end")
            
            # Process command in background
            threading.Thread(target=self._process_command, args=(command,), daemon=True).start()
    
    def _process_command(self, command):
        """Process command in background"""
        try:
            # Show thinking status
            self._set_status('thinking', True)
            
            response = self.command_processor.process(command)
            
            if response:
                self._add_message('ai', f"KARMA: {response}")
            
        except Exception as e:
            self.logger.error(f"Command error: {e}")
            self._add_message('error', f"Error: {str(e)}")
        
        finally:
            self._set_status('thinking', False)
    
    def _start_listening(self):
        """Start voice listening"""
        self._set_status('listening', True)
        threading.Thread(target=self._listen_loop, daemon=True).start()
    
    def _listen_loop(self):
        """Listen loop"""
        try:
            command = self.voice_engine.listen_for_command(timeout=5)
            if command:
                self._add_message('user', f"You: {command}")
                self._process_command(command)
        finally:
            self._set_status('listening', False)
    
    def _test_voice(self):
        """Test voice output"""
        self.voice_engine.speak("Hello! I am KARMA. Your personal AI assistant.")
    
    def _show_settings(self):
        """Show settings window"""
        settings = ctk.CTkToplevel(self.root)
        settings.title("KARMA Settings")
        settings.geometry("400x500")
        settings.configure(fg_color=self.colors['bg_dark'])
        
        ctk.CTkLabel(
            settings,
            text="Settings Panel",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors['neon_blue']
        ).pack(pady=20)
        
        ctk.CTkLabel(
            settings,
            text="Settings coming soon!",
            text_color=self.colors['text_secondary']
        ).pack()
    
    def _set_status(self, status, active):
        """Update status indicator"""
        if status == 'listening':
            self.is_listening = active
            if active:
                self.listening_label.configure(text="LISTENING", text_color=self.colors['neon_blue'])
                self.listening_canvas.itemconfig(self.listening_circle, fill=self.colors['neon_blue'])
                self._animate_listening()
            else:
                self.listening_label.configure(text="IDLE", text_color=self.colors['text_secondary'])
                self.listening_canvas.itemconfig(self.listening_circle, fill=self.colors['bg_light'])
        
        elif status == 'thinking':
            self.is_thinking = active
            if active:
                self.thinking_label.configure(text="THINKING", text_color=self.colors['warning'])
                self.thinking_canvas.itemconfig(self.thinking_circle, fill=self.colors['warning'])
            else:
                self.thinking_label.configure(text="READY", text_color=self.colors['text_secondary'])
                self.thinking_canvas.itemconfig(self.thinking_circle, fill=self.colors['bg_light'])
        
        elif status == 'speaking':
            self.is_speaking = active
            if active:
                self.speaking_label.configure(text="SPEAKING", text_color=self.colors['success'])
                self.speaking_canvas.itemconfig(self.speaking_circle, fill=self.colors['success'])
            else:
                self.speaking_label.configure(text="READY", text_color=self.colors['text_secondary'])
                self.speaking_canvas.itemconfig(self.speaking_circle, fill=self.colors['bg_light'])
    
    def _add_message(self, tag, message):
        """Add message to chat"""
        self.chat_text.insert("end", message + "\n\n", tag)
        self.chat_text.see("end")
    
    def run(self):
        """Start the GUI main loop"""
        self.logger.info("Starting Enhanced GUI main loop")
        self.root.mainloop()
    
    def close(self):
        """Close the GUI"""
        self.running = False
        if self.root:
            self.root.quit()
            self.root.destroy()
