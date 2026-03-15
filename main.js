/**
 * KARMA AI - Web Interface JavaScript
 * Handles all frontend functionality including:
 * - API communication with Flask backend
 * - Voice recognition integration
 * - Real-time UI updates
 * - Animations and effects
 */

(function() {
    'use strict';

    // ============================================
    // Configuration
    // ============================================
    const API_BASE = '';
    const STATUS_POLL_INTERVAL = 1000; // 1 second

    // ============================================
    // State
    // ============================================
    let isListening = false;
    let isProcessing = false;
    let statusPolling = null;

    // ============================================
    // DOM Elements
    // ============================================
    const elements = {
        // Status indicators
        statusListening: document.getElementById('statusListening'),
        statusThinking: document.getElementById('statusThinking'),
        statusSpeaking: document.getElementById('statusSpeaking'),
        statusOnline: document.getElementById('statusOnline'),
        
        // AI Orb
        aiOrb: document.getElementById('aiOrb'),
        aiStatusText: document.getElementById('aiStatusText'),
        logoOrb: document.getElementById('logoOrb'),
        
        // Input
        commandInput: document.getElementById('commandInput'),
        sendBtn: document.getElementById('sendBtn'),
        
        // Buttons
        micBtn: document.getElementById('micBtn'),
        testVoiceBtn: document.getElementById('testVoiceBtn'),
        tasksBtn: document.getElementById('tasksBtn'),
        helpBtn: document.getElementById('helpBtn'),
        settingsBtn: document.getElementById('settingsBtn'),
        
        // Panels
        commandHistory: document.getElementById('commandHistory'),
        responseContent: document.getElementById('responseContent'),
        
        // Time
        timeDisplay: document.getElementById('timeDisplay'),
        
        // Modals
        settingsModal: document.getElementById('settingsModal'),
        helpModal: document.getElementById('helpModal'),
        tasksModal: document.getElementById('tasksModal'),
        
        // Modal close buttons
        closeSettings: document.getElementById('closeSettings'),
        closeHelp: document.getElementById('closeHelp'),
        closeTasks: document.getElementById('closeTasks'),
        
        // Settings
        voiceRate: document.getElementById('voiceRate'),
        voiceRateValue: document.getElementById('voiceRateValue'),
        voiceVolume: document.getElementById('voiceVolume'),
        voiceVolumeValue: document.getElementById('voiceVolumeValue'),
        micSensitivity: document.getElementById('micSensitivity'),
        micSensitivityValue: document.getElementById('micSensitivityValue'),
        saveSettings: document.getElementById('saveSettings'),
        testSettings: document.getElementById('testSettings'),
        
        // Tasks
        newTaskInput: document.getElementById('newTaskInput'),
        addTaskBtn: document.getElementById('addTaskBtn'),
        tasksList: document.getElementById('tasksList')
    };

    // ============================================
    // Initialization
    // ============================================
    function init() {
        console.log('🚀 KARMA AI Web Interface initializing...');
        
        // Set up event listeners
        setupEventListeners();
        
        // Start time display
        updateTime();
        setInterval(updateTime, 1000);
        
        // Start status polling
        startStatusPolling();
        
        // Focus command input
        elements.commandInput.focus();
        
        console.log('✅ KARMA AI ready!');
    }

    // ============================================
    // Event Listeners
    // ============================================
    function setupEventListeners() {
        // Command input
        elements.commandInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendCommand();
            }
        });
        
        // Send button
        elements.sendBtn.addEventListener('click', sendCommand);
        
        // Voice button
        elements.micBtn.addEventListener('click', toggleVoice);
        
        // Test voice button
        elements.testVoiceBtn.addEventListener('click', testVoice);
        
        // Tasks button
        elements.tasksBtn.addEventListener('click', function() {
            openModal(elements.tasksModal);
            loadTasks();
        });
        
        // Help button
        elements.helpBtn.addEventListener('click', function() {
            openModal(elements.helpModal);
        });
        
        // Settings button
        elements.settingsBtn.addEventListener('click', function() {
            openModal(elements.settingsModal);
        });
        
        // Modal close buttons
        elements.closeSettings.addEventListener('click', function() {
            closeModal(elements.settingsModal);
        });
        
        elements.closeHelp.addEventListener('click', function() {
            closeModal(elements.helpModal);
        });
        
        elements.closeTasks.addEventListener('click', function() {
            closeModal(elements.tasksModal);
        });
        
        // Close modal on background click
        [elements.settingsModal, elements.helpModal, elements.tasksModal].forEach(modal => {
            modal.addEventListener('click', function(e) {
                if (e.target === modal) {
                    closeModal(modal);
                }
            });
        });
        
        // Settings sliders
        elements.voiceRate.addEventListener('input', function() {
            elements.voiceRateValue.textContent = this.value;
        });
        
        elements.voiceVolume.addEventListener('input', function() {
            elements.voiceVolumeValue.textContent = this.value + '%';
        });
        
        elements.micSensitivity.addEventListener('input', function() {
            elements.micSensitivityValue.textContent = this.value;
        });
        
        // Save settings
        elements.saveSettings.addEventListener('click', saveSettings);
        
        // Test voice
        elements.testSettings.addEventListener('click', function() {
            speakText("Hello! I am KARMA AI. Your personal assistant.");
        });
        
        // Add task
        elements.addTaskBtn.addEventListener('click', addTask);
        elements.newTaskInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                addTask();
            }
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            // Escape to close modals
            if (e.key === 'Escape') {
                closeAllModals();
            }
            
            // Ctrl + M for microphone
            if (e.ctrlKey && e.key === 'm') {
                e.preventDefault();
                toggleVoice();
            }
            
            // Ctrl + K to focus command input
            if (e.ctrlKey && e.key === 'k') {
                e.preventDefault();
                elements.commandInput.focus();
            }
        });
    }

    // ============================================
    // Time Display
    // ============================================
    function updateTime() {
        const now = new Date();
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');
        elements.timeDisplay.textContent = `${hours}:${minutes}:${seconds}`;
    }

    // ============================================
    // API Functions
    // ============================================
    
    /**
     * Send command to KARMA AI
     */
    async function sendCommand() {
        const command = elements.commandInput.value.trim();
        if (!command || isProcessing) return;
        
        // Clear input
        elements.commandInput.value = '';
        
        // Add to history
        addToHistory(command, 'user');
        
        // Set processing state
        setProcessingState(true);
        
        try {
            const response = await fetch(API_BASE + '/api/command', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ command: command })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Show response with typing animation
                addResponse(data.response, 'ai');
            } else {
                addResponse(data.error || 'An error occurred', 'ai', true);
            }
            
        } catch (error) {
            console.error('Command error:', error);
            addResponse('Failed to connect to KARMA AI', 'ai', true);
        } finally {
            setProcessingState(false);
        }
    }

    /**
     * Toggle voice recognition
     */
    async function toggleVoice() {
        if (isListening) {
            // Stop listening
            await stopListening();
        } else {
            // Start listening
            await startListening();
        }
    }

    /**
     * Start voice recognition
     */
    async function startListening() {
        try {
            const response = await fetch(API_BASE + '/api/voice/start', {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (data.success) {
                isListening = true;
                elements.micBtn.classList.add('active');
                setAIState('listening');
                elements.aiStatusText.textContent = 'Listening...';
            }
            
        } catch (error) {
            console.error('Voice start error:', error);
            showToast('Failed to start voice recognition', 'error');
        }
    }

    /**
     * Stop voice recognition
     */
    async function stopListening() {
        try {
            await fetch(API_BASE + '/api/voice/stop', {
                method: 'POST'
            });
            
            isListening = false;
            elements.micBtn.classList.remove('active');
            setAIState('ready');
            elements.aiStatusText.textContent = 'Ready';
            
        } catch (error) {
            console.error('Voice stop error:', error);
        }
    }

    /**
     * Test voice output
     */
    async function testVoice() {
        await speakText("Hello! I am KARMA AI. Your personal AI assistant, inspired by JARVIS from Iron Man.");
    }

    /**
     * Make KARMA speak text
     */
    async function speakText(text) {
        try {
            await fetch(API_BASE + '/api/speak', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text: text })
            });
        } catch (error) {
            console.error('Speak error:', error);
        }
    }

    /**
     * Get status from server
     */
    async function getStatus() {
        try {
            const response = await fetch(API_BASE + '/api/status');
            return await response.json();
        } catch (error) {
            console.error('Status error:', error);
            return null;
        }
    }

    /**
     * Load tasks
     */
    async function loadTasks() {
        try {
            const response = await fetch(API_BASE + '/api/tasks');
            const data = await response.json();
            
            if (data.success && data.tasks && data.tasks.length > 0) {
                renderTasks(data.tasks);
            } else {
                elements.tasksList.innerHTML = '<div class="tasks-empty">No tasks yet</div>';
            }
        } catch (error) {
            console.error('Load tasks error:', error);
            elements.tasksList.innerHTML = '<div class="tasks-empty">Failed to load tasks</div>';
        }
    }

    /**
     * Add new task
     */
    async function addTask() {
        const taskText = elements.newTaskInput.value.trim();
        if (!taskText) return;
        
        elements.newTaskInput.value = '';
        
        // Add task via command
        await sendCommandInternal('add task ' + taskText);
        
        // Reload tasks
        setTimeout(loadTasks, 500);
    }

    /**
     * Send command internally (for tasks etc.)
     */
    async function sendCommandInternal(command) {
        try {
            await fetch(API_BASE + '/api/command', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ command: command })
            });
        } catch (error) {
            console.error('Internal command error:', error);
        }
    }

    // ============================================
    // UI State Management
    // ============================================
    
    /**
     * Set processing state
     */
    function setProcessingState(processing) {
        isProcessing = processing;
        
        if (processing) {
            elements.sendBtn.disabled = true;
            elements.sendBtn.classList.add('loading');
            setAIState('thinking');
            elements.aiStatusText.textContent = 'Thinking...';
        } else {
            elements.sendBtn.disabled = false;
            elements.sendBtn.classList.remove('loading');
            setAIState('ready');
            elements.aiStatusText.textContent = 'Ready';
        }
    }

    /**
     * Set AI orb state
     */
    function setAIState(state) {
        // Remove all state classes
        elements.aiOrb.classList.remove('listening', 'thinking', 'speaking', 'ready');
        
        // Add new state class
        elements.aiOrb.classList.add(state);
        
        // Update status indicators
        updateStatusIndicators(state);
    }

    /**
     * Update status indicators
     */
    function updateStatusIndicators(state) {
        // Reset all
        elements.statusListening.classList.remove('listening');
        elements.statusThinking.classList.remove('thinking');
        elements.statusSpeaking.classList.remove('speaking');
        
        // Set active based on state
        switch(state) {
            case 'listening':
                elements.statusListening.classList.add('listening');
                break;
            case 'thinking':
                elements.statusThinking.classList.add('thinking');
                break;
            case 'speaking':
                elements.statusSpeaking.classList.add('speaking');
                break;
        }
    }

    /**
     * Start status polling
     */
    function startStatusPolling() {
        statusPolling = setInterval(async function() {
            const status = await getStatus();
            if (status) {
                // Update online indicator
                if (status.status === 'online') {
                    elements.statusOnline.classList.add('active');
                }
                
                // Update listening state
                if (status.is_listening && !isListening) {
                    isListening = true;
                    elements.micBtn.classList.add('active');
                    setAIState('listening');
                    elements.aiStatusText.textContent = 'Listening...';
                } else if (!status.is_listening && isListening && !isProcessing) {
                    isListening = false;
                    elements.micBtn.classList.remove('active');
                    setAIState('ready');
                    elements.aiStatusText.textContent = 'Ready';
                }
            }
        }, STATUS_POLL_INTERVAL);
    }

    // ============================================
    // History & Responses
    // ============================================
    
    /**
     * Add command to history
     */
    function addToHistory(command, type) {
        const now = new Date();
        const time = now.toLocaleTimeString();
        
        // Remove empty state if present
        const emptyEl = elements.commandHistory.querySelector('.history-empty');
        if (emptyEl) {
            emptyEl.remove();
        }
        
        const item = document.createElement('div');
        item.className = 'history-item';
        item.innerHTML = `
            <span class="command">${escapeHtml(command)}</span>
            <span class="timestamp">${time}</span>
        `;
        
        // Add to top
        elements.commandHistory.insertBefore(item, elements.commandHistory.firstChild);
        
        // Limit history items
        const items = elements.commandHistory.querySelectorAll('.history-item');
        if (items.length > 20) {
            items[items.length - 1].remove();
        }
    }

    /**
     * Add AI response
     */
    function addResponse(text, type, isError = false) {
        // Remove welcome message if present
        const welcomeEl = elements.responseContent.querySelector('.response-welcome');
        if (welcomeEl) {
            welcomeEl.remove();
        }
        
        const message = document.createElement('div');
        message.className = `response-message ${type}`;
        
        if (type === 'ai' && !isError) {
            message.classList.add('typing');
        }
        
        const label = type === 'user' ? 'You' : 'KARMA';
        const labelClass = isError ? 'error' : '';
        
        message.innerHTML = `
            <div class="label ${labelClass}">${label}</div>
            <div class="text">${escapeHtml(text)}</div>
        `;
        
        elements.responseContent.appendChild(message);
        
        // Remove typing class after animation
        if (type === 'ai') {
            setTimeout(() => {
                message.classList.remove('typing');
            }, text.length * 50); // Rough typing duration
        }
        
        // Scroll to bottom
        elements.responseContent.scrollTop = elements.responseContent.scrollHeight;
        
        // Add to history if AI response
        if (type === 'ai') {
            addToHistory(text, 'ai');
        }
    }

    /**
     * Render tasks
     */
    function renderTasks(tasks) {
        if (!tasks || tasks.length === 0) {
            elements.tasksList.innerHTML = '<div class="tasks-empty">No tasks yet</div>';
            return;
        }
        
        elements.tasksList.innerHTML = tasks.map(task => `
            <div class="task-item" data-id="${task.id}">
                <span class="task-text">${escapeHtml(task.task)}</span>
                <span class="task-delete" onclick="deleteTask(${task.id})">&times;</span>
            </div>
        `).join('');
    }

    // ============================================
    // Modal Management
    // ============================================
    
    function openModal(modal) {
        modal.classList.add('active');
    }
    
    function closeModal(modal) {
        modal.classList.remove('active');
    }
    
    function closeAllModals() {
        [elements.settingsModal, elements.helpModal, elements.tasksModal].forEach(modal => {
            modal.classList.remove('active');
        });
    }

    // ============================================
    // Settings
    // ============================================
    
    function saveSettings() {
        // In a full implementation, these would be saved to localStorage
        // or sent to the backend
        localStorage.setItem('karma_voiceRate', elements.voiceRate.value);
        localStorage.setItem('karma_voiceVolume', elements.voiceVolume.value);
        localStorage.setItem('karma_micSensitivity', elements.micSensitivity.value);
        
        showToast('Settings saved!', 'success');
        closeModal(elements.settingsModal);
    }

    function loadSettings() {
        if (localStorage.getItem('karma_voiceRate')) {
            elements.voiceRate.value = localStorage.getItem('karma_voiceRate');
            elements.voiceRateValue.textContent = elements.voiceRate.value;
        }
        
        if (localStorage.getItem('karma_voiceVolume')) {
            elements.voiceVolume.value = localStorage.getItem('karma_voiceVolume');
            elements.voiceVolumeValue.textContent = elements.voiceVolume.value + '%';
        }
        
        if (localStorage.getItem('karma_micSensitivity')) {
            elements.micSensitivity.value = localStorage.getItem('karma_micSensitivity');
            elements.micSensitivityValue.textContent = elements.micSensitivity.value;
        }
    }

    // ============================================
    // Toast Notifications
    // ============================================
    
    function showToast(message, type = 'info') {
        // Create container if not exists
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
        
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        
        container.appendChild(toast);
        
        // Remove after 3 seconds
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }

    // ============================================
    // Utilities
    // ============================================
    
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // ============================================
    // Global Functions (for onclick handlers)
    // ============================================
    window.deleteTask = async function(taskId) {
        await sendCommandInternal('delete task ' + taskId);
        setTimeout(loadTasks, 500);
    };

    // ============================================
    // Initialize on DOM Ready
    // ============================================
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Load saved settings
    loadSettings();

})();
