"""
text_to_speech.py  —  AURA-X Voice Engine
Uses Microsoft Edge TTS (neural voices, free, no API key needed).
Falls back to pyttsx3 if offline or Edge TTS fails.

Install dependency:  pip install edge-tts
"""

import asyncio
import os
import re
import tempfile


# ── Voice config ──────────────────────────────────────────────────────────────
# Best Jarvis-like voices to try:
#   "en-US-GuyNeural"        — deep, calm, professional (closest to Jarvis)
#   "en-US-ChristopherNeural"— authoritative, smooth
#   "en-US-EricNeural"       — clear, neutral
#   "en-GB-RyanNeural"       — British, sharp (very Jarvis-esque)
#   "en-GB-ThomasNeural"     — British, composed

VOICE        = "en-US-ChristopherNeural"   # 🔥 Change this to try different voices
RATE         = "+8%"                # slightly faster than default (+0%)
PITCH        = "-5Hz"               # slightly lower = more authoritative
VOLUME       = "+0%"


# ── Text pre-processing ───────────────────────────────────────────────────────

def _preprocess(text: str) -> str:
    """
    Make the TTS output feel more natural and Jarvis-like:
    - Clean up excessive punctuation
    - Add natural pauses at sentence breaks
    - Expand common abbreviations
    - Remove markdown/symbols that TTS reads literally
    """
    # Strip markdown bold/italic
    text = re.sub(r"\*{1,2}(.*?)\*{1,2}", r"\1", text)
    text = re.sub(r"_{1,2}(.*?)_{1,2}", r"\1", text)

    # Remove code blocks
    text = re.sub(r"```.*?```", "code block omitted", text, flags=re.DOTALL)
    text = re.sub(r"`(.*?)`", r"\1", text)

    # Expand common abbreviations for natural reading
    replacements = {
        r"\bAI\b":      "A.I.",
        r"\bAPI\b":     "A.P.I.",
        r"\bURL\b":     "U.R.L.",
        r"\bUI\b":      "U.I.",
        r"\bOS\b":      "O.S.",
        r"\be\.g\.\b":  "for example",
        r"\bi\.e\.\b":  "that is",
        r"\betc\.\b":   "et cetera",
        r"\bvs\.\b":    "versus",
        r"\bDr\.\b":    "Doctor",
        r"\bMr\.\b":    "Mister",
        r"\bMs\.\b":    "Miss",
    }
    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text)

    # Natural pauses — SSML-style pause via comma tricks
    text = text.replace("...", ", ")
    text = text.replace(" - ", ", ")

    # Clean up extra whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text


# ── Core async TTS ───────────────────────────────────────────────────────────

async def _speak_edge(text: str):
    try:
        import edge_tts
        import pygame
    except ImportError:
        raise ImportError("edge_tts or pygame not installed")

    text = _preprocess(text)

    # Write audio to a temp file
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tmp_path = tmp.name
    tmp.close()

    communicate = edge_tts.Communicate(
        text,
        voice=VOICE,
        rate=RATE,
        pitch=PITCH,
        volume=VOLUME,
    )
    await communicate.save(tmp_path)

    # Play with pygame (non-blocking within this thread)
    pygame.mixer.init()
    pygame.mixer.music.load(tmp_path)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        await asyncio.sleep(0.05)

    pygame.mixer.music.stop()
    pygame.mixer.quit()
    os.unlink(tmp_path)


# ── Fallback: pyttsx3 ────────────────────────────────────────────────────────

def _speak_fallback(text: str):
    """pyttsx3 fallback if Edge TTS is unavailable (offline)."""
    import pyttsx3
    text = _preprocess(text)
    engine = pyttsx3.init()
    engine.setProperty("rate", 165)
    engine.setProperty("volume", 1.0)
    voices = engine.getProperty("voices")
    # prefer index 1 (female) — swap to 0 for male SAPI voice
    if len(voices) > 1:
        engine.setProperty("voice", voices[1].id)
    engine.say(text)
    engine.runAndWait()
    engine.stop()


# ── Public API ────────────────────────────────────────────────────────────────

def speak(text: str):
    """
    Speak text using Edge TTS neural voice.
    Automatically falls back to pyttsx3 if Edge TTS fails.
    """
    if not text or not text.strip():
        return

    try:
        # Edge TTS needs an event loop — create one if needed
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                raise RuntimeError
            loop.run_until_complete(_speak_edge(text))
        except RuntimeError:
            asyncio.run(_speak_edge(text))

    except Exception as e:
        print(f"[TTS] Edge TTS failed ({e}), using fallback.")
        _speak_fallback(text)