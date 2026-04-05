import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.text_to_speech import speak
speak("Hello Atharva")