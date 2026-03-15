"""
GUI Module for KARMA AI
Tkinter-based dashboard with status indicators and controls
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import logging
from datetime import datetime


class GUIDashboard:
    """
    GUI Dashboard for KARMA AI
    Features:
    - Status indicators (Listening, Thinking, Speaking)
    - Command input/output display
    - Control buttons
    - Settings panel
    """
    
    def __init__(self, voice_engine, command_processor, ai_brain, memory, logger=None):
        """Initialize GUI components"""
        self.logger = logger or logging.getLogger('KARMA-GUI')
        
        # Core components
        self.voice_engine = voice_engine
        self.command_processor = command_processor
        self.ai_brain = ai_brain
        self.memory = memory
        
        # State
        self.is_listening = False
        self.is_speaking = False
        self.is_thinking = False
        
        # Setup GUI
        self.root = None
        self._setup_gui()
        
        self.logger.info("GUI initialized")
    
    def _setup_gui(self):
        """Setup the GUI interface"""
        # Main window
        self.root = tk.Tk()
        self.root.title("KARMA AI - Personal Assistant")
        self.root.geometry("600x700")
        self.root.resizable(True, True)
        
        # Set dark theme colors
        self.bg_color = '#1e1e2e'
        self.fg_color = '#cdd6f4'
        self.accent_color = '#89b4fa'
        self.success_color = '#a6e3a1'
        self.warning_color = '#f9e2af'
        self.error_color = '#f38ba8'
        
        self.root.configure(bg=self.bg_color)
        
        # Configure styles
        self._configure_styles()
        
        # Create frames
        self._create_header()
        self._create_status_bar()
        self._create_chat_display()
        self._create_input_area()
        self._create_control_panel()
        self._create_menu()
    
    def _configure_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure button style
        style.configure(
            'Accent.TButton',
            background=self.accent_color,
            foreground=self.bg_color,
            font=('Segoe UI', 10, 'bold'),
            padding=10
        )
        
        # Configure label style
        style.configure(
            'Status.TLabel',
            background=self.bg_color,
            foreground=self.fg_color,
            font=('Segoe UI', 10)
        )
    
    def _create_header(self):
        """Create header section"""
        header_frame = tk.Frame(self.root, bg=self.bg_color, height=60)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Logo/Title
        title_label = tk.Label(
            header_frame,
            text="KARMA AI",
            font=('Segoe UI', 24, 'bold'),
            fg=self.accent_color,
            bg=self.bg_color
        )
        title_label.pack(side=tk.LEFT)
        
        # Subtitle
        subtitle = tk.Label(
            header_frame,
            text="Your Personal Assistant",
            font=('Segoe UI', 10),
            fg=self.fg_color,
            bg=self.bg_color
        )
        subtitle.pack(side=tk.LEFT, padx=10)
        
        # Time display
        self.time_label = tk.Label(
            header_frame,
            text="",
            font=('Segoe UI', 12),
            fg=self.fg_color,
            bg=self.bg_color
        )
        self.time_label.pack(side=tk.RIGHT)
        
        # Update time
        self._update_time()
    
    def _create_status_bar(self):
        """Create status indicator bar"""
        status_frame = tk.Frame(self.root, bg='#313244', height=50)
        status_frame.pack(fill=tk.X, padx=20, pady=5)
        
        # Status indicators
        self.status_indicators = {}
        
        statuses = [
            ('listening', 'Listening'),
            ('thinking', 'Thinking'),
            ('speaking', 'Speaking'),
            ('online', 'Online')
        ]
        
        for i, (key, label) in enumerate(statuses):
            # Frame for each status
            frame = tk.Frame(status_frame, bg='#313244')
            frame.pack(side=tk.LEFT, padx=20)
            
            # Indicator circle
            indicator = tk.Canvas(frame, width=15, height=15, bg='#313244', highlightthickness=0)
            indicator.pack(side=tk.LEFT)
            
            # Draw circle
            color = self.error_color if key != 'online' else self.success_color
            indicator.create_oval(2, 2, 13, 13, fill=color, outline='')
            
            # Label
            label_widget = tk.Label(
                frame,
                text=label,
                font=('Segoe UI', 9),
                fg=self.fg_color,
                bg='#313244'
            )
            label_widget.pack(side=tk.LEFT, padx=5)
            
            self.status_indicators[key] = {'indicator': indicator, 'label': label_widget, 'color': color}
    
    def _create_chat_display(self):
        """Create chat message display"""
        chat_frame = tk.Frame(self.root, bg=self.bg_color)
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Label
        chat_label = tk.Label(
            chat_frame,
            text="Conversation",
            font=('Segoe UI', 12, 'bold'),
            fg=self.fg_color,
            bg=self.bg_color
        )
        chat_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Text widget with scrollbar
        self.chat_text = scrolledtext.ScrolledText(
            chat_frame,
            font=('Consolas', 10),
            bg='#313244',
            fg=self.fg_color,
            wrap=tk.WORD,
            height=15,
            padx=10,
            pady=10
        )
        self.chat_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags
        self.chat_text.tag_config('user', foreground='#89b4fa')
        self.chat_text.tag_config('ai', foreground='#a6e3a1')
        self.chat_text.tag_config('system', foreground='#f9e2af')
        self.chat_text.tag_config('error', foreground='#f38ba8')
    
    def _create_input_area(self):
        """Create command input area"""
        input_frame = tk.Frame(self.root, bg=self.bg_color)
        input_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Label
        input_label = tk.Label(
            input_frame,
            text="Type Command:",
            font=('Segoe UI', 10),
            fg=self.fg_color,
            bg=self.bg_color
        )
        input_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Input field
        input_container = tk.Frame(input_frame, bg='#313244')
        input_container.pack(fill=tk.X)
        
        self.command_entry = tk.Entry(
            input_container,
            font=('Segoe UI', 11),
            bg='#313244',
            fg=self.fg_color,
            insertbackground=self.fg_color,
            relief=tk.FLAT,
            insertwidth=2
        )
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.command_entry.bind('<Return>', self._on_command_submit)
        
        # Send button
        send_button = tk.Button(
            input_container,
            text="Send",
            font=('Segoe UI', 10, 'bold'),
            bg=self.accent_color,
            fg=self.bg_color,
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=self._on_command_submit
        )
        send_button.pack(side=tk.RIGHT, padx=(10, 0))
    
    def _create_control_panel(self):
        """Create control buttons panel"""
        control_frame = tk.Frame(self.root, bg=self.bg_color)
        control_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Button labels
        buttons = [
            ('🎤 Listen', self._start_listening),
            ('⏹ Stop', self._stop_listening),
            ('🔊 Test Voice', self._test_voice),
            ('📋 View Tasks', self._show_tasks),
            ('⚙ Settings', self._show_settings),
        ]
        
        for i, (label, command) in enumerate(buttons):
            btn = tk.Button(
                control_frame,
                text=label,
                font=('Segoe UI', 9),
                bg='#45475a',
                fg=self.fg_color,
                relief=tk.FLAT,
                padx=15,
                pady=8,
                command=command,
                cursor='hand2'
            )
            btn.pack(side=tk.LEFT, padx=5)
            
            # Bind hover effects
            btn.bind('<Enter>', lambda e, b=btn: b.configure(bg=self.accent_color, fg=self.bg_color))
            btn.bind('<Leave>', lambda e, b=btn: b.configure(bg='#45475a', fg=self.fg_color))
    
    def _create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Clear Chat", command=self._clear_chat)
        file_menu.add_command(label="Export History", command=self._export_history)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Commands List", command=self._show_help)
        help_menu.add_command(label="About", command=self._show_about)
    
    def _update_time(self):
        """Update time display"""
        current_time = datetime.now().strftime("%I:%M %p")
        self.time_label.config(text=current_time)
        self.root.after(1000, self._update_time)
    
    def _on_command_submit(self, event=None):
        """Handle command submission"""
        command = self.command_entry.get().strip()
        if command:
            self._add_message('user', f"You: {command}")
            self.command_entry.delete(0, tk.END)
            
            # Process command
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
    
    def _stop_listening(self):
        """Stop listening"""
        self._set_status('listening', False)
        self.voice_engine.stop()
    
    def _test_voice(self):
        """Test voice output"""
        self.voice_engine.speak("Hello! I am KARMA. Your personal AI assistant.")
    
    def _show_tasks(self):
        """Show task list"""
        tasks = self.memory.get_tasks()
        if tasks:
            task_list = "\n".join([f"{t['id']}. {t['task']}" for t in tasks])
            messagebox.showinfo("Tasks", task_list)
        else:
            messagebox.showinfo("Tasks", "No tasks in your list!")
    
    def _show_settings(self):
        """Show settings window"""
        messagebox.showinfo("Settings", "Settings panel coming soon!")
    
    def _clear_chat(self):
        """Clear chat display"""
        self.chat_text.delete(1.0, tk.END)
    
    def _export_history(self):
        """Export conversation history"""
        # TODO: Implement export
        messagebox.showinfo("Export", "Export feature coming soon!")
    
    def _show_help(self):
        """Show help window"""
        help_text = """
KARMA AI Commands:

Voice Commands:
• "Hey Karma" - Activate voice mode
• "Open [website]" - Open websites
• "Play [song]" - Play music
• "Set volume [0-100]" - Control volume
• "What's the time/date?" - Get info

System Commands:
• "Shutdown/Restart" - Control system
• "Take a screenshot" - Screenshot
• "Open [app]" - Open applications

Task Management:
• "Add task [name]" - Add to todo
• "Show tasks" - View all tasks
• "Set alarm [time]" - Set alarm

AI Features:
• Ask questions
• Have conversations
• Get explanations
        """
        messagebox.showinfo("KARMA AI Help", help_text)
    
    def _show_about(self):
        """Show about window"""
        messagebox.showinfo("About KARMA AI", 
                           "KARMA AI v2.0\n\n"
                           "Advanced Personal AI Assistant\n"
                           "Inspired by JARVIS from Iron Man\n\n"
                           "Features:\n"
                           "• Voice Recognition\n"
                           "• AI Conversations\n"
                           "• System Automation\n"
                           "• Task Management")
    
    def _set_status(self, status, active):
        """Update status indicator"""
        if status in self.status_indicators:
            indicator = self.status_indicators[status]['indicator']
            color = self.status_indicators[status]['color']
            
            if active:
                color = self.success_color
            else:
                color = self.error_color if status != 'online' else self.success_color
            
            indicator.delete('all')
            indicator.create_oval(2, 2, 13, 13, fill=color, outline='')
    
    def _add_message(self, tag, message):
        """Add message to chat"""
        self.chat_text.insert(tk.END, message + '\n\n', tag)
        self.chat_text.see(tk.END)
    
    def run(self):
        """Start the GUI main loop"""
        self.logger.info("Starting GUI main loop")
        self.root.mainloop()
    
    def close(self):
        """Close the GUI"""
        if self.root:
            self.root.quit()
            self.root.destroy()
