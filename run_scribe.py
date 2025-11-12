"""
Scribe launcher - The Open Voice Platform
Modern successor to WhisperWriter
"""
import os
import sys
from dotenv import load_dotenv

# Add src to path so we can import scribe package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print('Starting Scribe - The Open Voice Platform')
print('Modern voice automation with Fluent UI')
print()

load_dotenv()

# Import and run the modern Scribe app
from scribe.__main__ import main

if __name__ == '__main__':
    main()
