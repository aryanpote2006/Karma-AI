# KARMA AI - Training Layer Integration Guide

## Overview
This document explains how to integrate the `karma_trainer.py` training module with your existing KARMA AI voice assistant.

---

## Files Created

1. **`karma_trainer.py`** - Training and intelligence layer module
2. **`training_data.json`** - Dataset with command phrase mappings

---

## Integration Options

### Option 1: Integrate with karma.py (Simple Entry Point)

Open `karma.py` and make the following changes:

#### Step 1: Import the trainer at the top of the file

```python
# Add this import after the existing imports
from karma_ai.karma_trainer import KarmaTrainer, get_command_string

# Initialize the trainer (add after music_lib initialization)
trainer = KarmaTrainer()
```

#### Step 2: Modify the processCommand function

Find the `processCommand(c)` function and add the trainer processing at the beginning:

```python
def processCommand(c):
    # Convert to lowercase for comparison
    c = c.lower()
    
    # ======= ADD THIS: Use trainer to improve command recognition =======
    # First, try to match using the trainer
    recognized_command = trainer.recognize(c)
    
    if recognized_command:
        # Convert canonical command to actual command string
        actual_command = get_command_string(recognized_command)
        if actual_command:
            c = actual_command  # Use the improved command
    # ======================================================================
    
    # ... rest of your existing processCommand function continues unchanged ...
```

---

### Option 2: Integrate with karma_ai/main.py (Advanced Entry Point)

The advanced entry point already uses `CommandProcessor`. Here's how to add the trainer layer:

#### Step 1: Import the trainer in karma_ai/main.py

```python
from karma_trainer import KarmaTrainer, get_command_string
```

#### Step 2: Initialize the trainer in KarmaAI.__init__

```python
# Add in the __init__ method after other initializations
self.trainer = KarmaTrainer()
```

#### Step 3: Modify _process_command method

Find the `_process_command` method and add the trainer processing:

```python
def _process_command(self, command):
    """Process user command"""
    self.is_thinking = True
    
    try:
        # ======= ADD THIS: Use trainer to improve command recognition =======
        recognized = self.trainer.recognize(command)
        
        if recognized:
            # Convert canonical command to actual command string
            actual_command = get_command_string(recognized)
            if actual_command:
                command = actual_command
        # =====================================================================
        
        response = self.command_processor.process(command)
        
        if response:
            self.is_speaking = True
            self.voice_engine.speak(response)
            self.is_speaking = False
            
    except Exception as e:
        self.logger.error(f"Command processing error: {e}")
        self.voice_engine.speak("Sorry, I encountered an error.")
    
    self.is_thinking = False
```

---

## How the Training Layer Works

```
Voice Input (e.g., "start youtube")
        │
        ▼
┌───────────────────┐
│  KarmaTrainer     │
│  predict_command()│
└───────────────────┘
        │
        ▼
   ┌────────────┐
   │ 1. Exact  │
   │    Match  │
   └────────────┘
        │
        ▼
   ┌────────────┐
   │ 2. Partial │
   │    Match  │
   └────────────┘
        │
        ▼
   ┌────────────┐
   │ 3. Fuzzy  │
   │  Matching │
   └────────────┘
        │
        ▼
   ┌────────────┐
   │ 4. TF-IDF │
   │ (sklearn) │
   └────────────┘
        │
        ▼
┌─────────────────────┐
│  Canonical Command  │
│  "open_youtube"     │
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│  get_command_string │
│  "open youtube"      │
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│  Original Code      │
│  processCommand()    │
└─────────────────────┘
```

---

## Handling Unrecognized Commands

When the trainer cannot match a command, it returns `None`. Your original code will handle it as an unknown command. Optionally, you can add a response:

```python
# After trainer processing, add this check:
if not recognized_command:
    # Optional: Provide feedback for unrecognized commands
    # speak("I didn't understand that. Please say it again clearly.")
    pass
```

---

## Adding Custom Training Phrases

You can extend the training data dynamically:

```python
from karma_trainer import KarmaTrainer

trainer = KarmaTrainer()

# Add new phrases for an existing command
trainer.train("open_youtube", [
    "load youtube",
    "go to video site",
    "start watching videos"
])

# Save to training_data.json
trainer.save_training_data()
```

---

## Testing the Trainer

Run the trainer module directly to test:

```bash
cd karma_ai
python karma_trainer.py
```

This will show sample phrase recognitions.

---

## Dependencies

The trainer works with or without scikit-learn:

- **Without sklearn**: Uses string matching (exact, partial, fuzzy)
- **With sklearn**: Adds TF-IDF semantic matching for better recognition

To install sklearn (optional but recommended):
```bash
pip install scikit-learn
```

---

## Important Notes

1. **No code changes required to existing commands**: The trainer maps phrases to your existing command strings
2. **Backward compatible**: If trainer fails to recognize, falls back to original code
3. **Extensible**: Add more phrases to `training_data.json` anytime
4. **Non-destructive**: Original code logic remains unchanged

---

## Quick Integration Checklist

- [ ] Copy `karma_trainer.py` to `karma_ai/` folder
- [ ] Copy `training_data.json` to `karma_ai/` folder
- [ ] Import trainer in your entry point
- [ ] Initialize trainer instance
- [ ] Add trainer.recognize() call before command processing
- [ ] Use get_command_string() to convert to actual command
- [ ] Test with phrases like "start youtube", "launch chrome"

---

## Support

If you need help with integration, the trainer includes:
- Detailed logging for debugging
- Graceful fallback to original code
- Support for both entry points (karma.py and karma_ai/main.py)

