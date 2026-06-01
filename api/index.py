import os
import sys

# Ensure the root project directory is on the python search path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
