"""Add Smart Web Mode - Auto Google search for unknown commands"""

# Read the file
with open('command_processor.py', 'r') as f:
    content = f.read()

# Update the fallback to do Google search instead of saying "I'm not sure"
old_fallback = '''        # Default response for unrecognized commands
        return "I'm not sure how to help with that. Could you try rephrasing?"'''

new_fallback = '''        # Smart Web Mode - If command not recognized, search on Google
        try:
            search_query = command.strip()
            self.automation.internet_search(search_query)
            return f"I couldn't find a command for that, but I searched for: {search_query}"
        except:
            return "I'm not sure how to help with that. Could you try rephrasing?"'''

content = content.replace(old_fallback, new_fallback)

# Write back
with open('command_processor.py', 'w') as f:
    f.write(content)

print("Added Smart Web Mode to command_processor.py!")
