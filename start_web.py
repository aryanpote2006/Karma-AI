"""
KARMA AI Web Interface Launcher
Run this script to start the modern web interface
"""

import os
import sys

# Change to project root
project_root = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_root)

# Add paths
sys.path.insert(0, project_root)

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Starting KARMA AI Web Interface")
    print("=" * 60)
    print("\n📍 Opening http://localhost:5000 in your browser...\n")
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Run the Flask app
    from web.app import app
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
