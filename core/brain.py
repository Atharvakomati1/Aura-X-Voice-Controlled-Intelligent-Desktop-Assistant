# import webbrowser
# import os
# import subprocess
# from services.ai_service import ask_ai
# from core.app_control import open_app

# last_opened_app= None
# awaiting_song=False

# def is_detailed_request(command):
#     keywords = ["explain", "detail", "in depth", "deep"]
#     return any(word in command.lower() for word in keywords)

# # def process_command(command):
# #     command = command.lower()

# #     # 🔥 SYSTEM COMMANDS
# #     if "open youtube" in command:
# #         webbrowser.open("https://youtube.com")
# #         return "Opening YouTube"

# #     elif "open google" in command:
# #         webbrowser.open("https://google.com")
# #         return "Opening Google"

# #     elif "open github" in command:
# #         webbrowser.open("https://github.com")
# #         return "Opening GitHub"

# #     elif "open notepad" in command:
# #         os.system("notepad")
# #         return "Opening Notepad"

# #     elif "time" in command:
# #         from datetime import datetime
# #         return f"The time is {datetime.now().strftime('%I:%M %p')}"

# #     if is_detailed_request(command):
# #         return ask_ai(command + " Give a detailed explanation.")
# #     else:
# #         return ask_ai(command)



# import webbrowser

# def handle_search(command):
    
    

#     command = command.lower()

#     if "search" in command:
#         query = command.replace("search", "").strip()

#         # 🔥 PRIORITY: explicit command
#         if "youtube" in command:
#             url = f"https://www.youtube.com/results?search_query={query}"
#             webbrowser.open(url)
#             last_opened_app = "youtube"
#             return f"Searching YouTube for {query}"

#         if "google" in command:
#             url = f"https://www.google.com/search?q={query}"
#             webbrowser.open(url)
#             last_opened_app = "google"
#             return f"Searching Google for {query}"

#         # 🔥 FALLBACK: last opened app
#         if last_opened_app == "youtube":
#             url = f"https://www.youtube.com/results?search_query={query}"
#             webbrowser.open(url)
#             return f"Searching YouTube for {query}"

#         # default Google
#         url = f"https://www.google.com/search?q={query}"
#         webbrowser.open(url)
#         return f"Searching Google for {query}"

#     return None

# def process_command(command):
#     global awaiting_song
#     global last_opened_app
#     command = command.lower()
#     # 🔥 MULTI-COMMAND SPLIT
#     if " and " in command:
#         parts = command.split(" and ")
#         responses = []

#         for part in parts:
#             result = process_command(part.strip())
#             if result:
#                 responses.append(result)

#         return ". ".join(responses)
#     # 🔍 SEARCH HANDLING
#     search_result = handle_search(command)
#     if search_result:
#         return search_result

#     # 🌐 OPEN WEBSITES
#     if "open youtube" in command:
#         webbrowser.open("https://youtube.com")
#         global last_opened_app
#         last_opened_app = "youtube"
#         return "Opening YouTube"

#     if "open google" in command:
#         webbrowser.open("https://google.com")

#         # global last_opened_app
#         last_opened_app = "google"   # ✅ ADD THIS

#         return "Opening Google"
    
#     # 🎵 MUSIC FEATURE
#     if "play song" in command or "play music" in command:
#         awaiting_song = True
#         return "Which song would you like to play?"

#     # 🎵 If waiting for song name
#     if awaiting_song:
#         awaiting_song = False

#         song = command.strip().replace("play", "").strip()

#         import webbrowser
#         query = song.replace(" ", "%20")

#         url = f"https://open.spotify.com/search/{query}"
#         webbrowser.open(url)

#         return f"Playing {song} on Spotify"

    
#     if "open github" in command:
#         webbrowser.open("https://github.com")
#         return "Opening GitHub"

#     # 🖥️ OPEN APPS (Windows)
#     if "open chrome" in command:
#         os.system("start chrome")
#         return "Opening Chrome"

#     if "open notepad" in command:
#         os.system("notepad")
#         return "Opening Notepad"

#     if "open calculator" in command:
#         os.system("calc")
#         return "Opening Calculator"

#     if "open vs code" in command or "open vscode" in command:
#         os.system("code")
#         return "Opening Visual Studio Code"

#     # ❌ CLOSE APPS
#     if "close chrome" in command:
#         os.system("taskkill /f /im chrome.exe")
#         return "Closing Chrome"

#     if "close notepad" in command:
#         os.system("taskkill /f /im notepad.exe")
#         return "Closing Notepad"

#     if "close vs code" in command:
#         os.system("taskkill /f /im Code.exe")
#         return "Closing VS Code"

#     # ⏰ TIME
#     if "time" in command:
#         from datetime import datetime
#         return f"It’s {datetime.now().strftime('%I:%M %p')}"
    
#     # 🔥 DYNAMIC APP OPEN
#     if command.startswith("open "):
#         app_name = command.replace("open ", "").strip()

#         result = open_app(app_name)
#         if result:
#             return result
    
#     # fallback to AI
#     return ask_ai(command)
    

import webbrowser
import os
import subprocess
from services.ai_service import ask_ai
from core.app_control import open_app
from dotenv import load_dotenv
load_dotenv()

last_opened_app = None
awaiting_song = False

# ── Spotify credentials ───────────────────────────────────────────────────────
# Get these from https://developer.spotify.com/dashboard
# 1. Log in → Create App → any name → Redirect URI: http://localhost:8888
# 2. Paste your Client ID and Secret below
SPOTIFY_CLIENT_ID     = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")



def is_detailed_request(command):
    keywords = ["explain", "detail", "in depth", "deep"]
    return any(word in command.lower() for word in keywords)


def handle_search(command):
    command = command.lower()

    if "search" in command:
        query = command.replace("search", "").strip()

        if "youtube" in command:
            url = f"https://www.youtube.com/results?search_query={query}"
            webbrowser.open(url)
            return f"Searching YouTube for {query}"

        if "google" in command:
            url = f"https://www.google.com/search?q={query}"
            webbrowser.open(url)
            return f"Searching Google for {query}"

        if last_opened_app == "youtube":
            url = f"https://www.youtube.com/results?search_query={query}"
            webbrowser.open(url)
            return f"Searching YouTube for {query}"

        url = f"https://www.google.com/search?q={query}"
        webbrowser.open(url)
        return f"Searching Google for {query}"

    return None


def _get_track_uri(song: str) -> str | None:
    """
    Uses Spotify's Search API (no Premium needed) to find the
    exact track URI for a song name.
    Returns e.g. "spotify:track:6rqhFgbbKwnb9MLmUQDhG6" or None on failure.
    """
    try:
        import spotipy
        from spotipy.oauth2 import SpotifyClientCredentials

        sp = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=SPOTIFY_CLIENT_ID,
                client_secret=SPOTIFY_CLIENT_SECRET,
            )
        )
        results = sp.search(q=song, type="track", limit=1)
        tracks = results.get("tracks", {}).get("items", [])
        if tracks:
            return tracks[0]["uri"]          # e.g. "spotify:track:XXXX"
    except Exception as e:
        print(f"[Spotify Search] {e}")
    return None


def _ensure_spotify_running() -> bool:
    """
    Launches Spotify desktop app if not already running.
    Returns True if launched or already running.
    """
    spotify_paths = [
        os.path.expandvars(r"%APPDATA%\Spotify\Spotify.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WindowsApps\Spotify.exe"),
        r"C:\Program Files\Spotify\Spotify.exe",
    ]
    for path in spotify_paths:
        if os.path.exists(path):
            subprocess.Popen([path])
            return True
    try:
        os.system("start spotify")
        return True
    except Exception:
        return False


def open_spotify_and_play(song: str) -> str:
    """
    Finds the exact Spotify track URI via search API, then opens
    the installed Spotify app directly on that track.

    Flow:
      1. Query Spotify Search API → get spotify:track:<id>
      2. Ensure Spotify.exe is running
      3. Open the track URI → Spotify jumps straight to the song and plays it
      4. Fallback to spotify:search: if API lookup fails
    """
    song = song.strip()

    if not song:
        # Just open Spotify with no song
        _ensure_spotify_running()
        return "Opening Spotify"

    print(f"[Spotify] Looking up track: {song}")

    #Step 1: Get the exact track URI 
    track_uri = _get_track_uri(song)

    if track_uri:
        uri = track_uri                         
        msg = f"Playing '{song}' on Spotify"
        print(f"[Spotify] Found URI: {uri}")
    else:
        # Fallback: open search page in app (better than nothing)
        uri = "spotify:search:" + song.replace(" ", "%20")
        msg = f"Searching '{song}' on Spotify (couldn't find exact match)"
        print(f"[Spotify] Falling back to search URI")

    # ── Step 2: Make sure Spotify is open ────────────────────
    # Check if already running first to avoid double-launch
    import subprocess
    result = subprocess.run(
        ["tasklist", "/fi", "imagename eq Spotify.exe"],
        capture_output=True, text=True
    )
    already_running = "Spotify.exe" in result.stdout

    if not already_running:
        _ensure_spotify_running()
        import time
        time.sleep(2.5)   # wait for Spotify to finish starting

    # ── Step 3: Fire the URI — Spotify opens directly on the track ──
    try:
        webbrowser.open(uri)
        return msg
    except Exception as e:
        return f"Spotify opened but couldn't play '{song}'. Error: {e}"


def process_command(command):
    global awaiting_song, last_opened_app
    command = command.lower()

    # ── MULTI-COMMAND SPLIT ──────────────────────────────────
    if " and " in command:
        parts = command.split(" and ")
        responses = []
        for part in parts:
            result = process_command(part.strip())
            if result:
                responses.append(result)
        return ". ".join(responses)

    # ── SEARCH ───────────────────────────────────────────────
    search_result = handle_search(command)
    if search_result:
        return search_result

    # ── OPEN WEBSITES ────────────────────────────────────────
    if "open youtube" in command:
        webbrowser.open("https://youtube.com")
        last_opened_app = "youtube"
        return "Opening YouTube"

    if "open google" in command:
        webbrowser.open("https://google.com")
        last_opened_app = "google"
        return "Opening Google"

    if "open github" in command:
        webbrowser.open("https://github.com")
        return "Opening GitHub"

    # ── MUSIC ────────────────────────────────────────────────
    if "play song" in command or "play music" in command:
        awaiting_song = True
        return "Which song would you like to play?"

    if command.startswith("play ") and not awaiting_song:
        song = command.replace("play ", "", 1).strip()
        if song:
            return open_spotify_and_play(song)

    if awaiting_song:
        awaiting_song = False
        song = command.strip()
        return open_spotify_and_play(song)

    # ── OPEN / CLOSE SPOTIFY ─────────────────────────────────
    if "open spotify" in command:
        return open_spotify_and_play("")

    if "close spotify" in command:
        os.system("taskkill /f /im Spotify.exe")
        return "Closing Spotify"

    # ── OPEN APPS ────────────────────────────────────────────
    if "open chrome" in command:
        os.system("start chrome")
        return "Opening Chrome"

    if "open notepad" in command:
        os.system("notepad")
        return "Opening Notepad"

    if "open calculator" in command:
        os.system("calc")
        return "Opening Calculator"

    if "open vs code" in command or "open vscode" in command:
        os.system("code")
        return "Opening Visual Studio Code"

    # ── CLOSE APPS ───────────────────────────────────────────
    if "close chrome" in command:
        os.system("taskkill /f /im chrome.exe")
        return "Closing Chrome"

    if "close notepad" in command:
        os.system("taskkill /f /im notepad.exe")
        return "Closing Notepad"

    if "close vs code" in command:
        os.system("taskkill /f /im Code.exe")
        return "Closing VS Code"

    # ── TIME ─────────────────────────────────────────────────
    if "time" in command:
        from datetime import datetime
        return f"It's {datetime.now().strftime('%I:%M %p')}"

    # ── DYNAMIC APP OPEN ─────────────────────────────────────
    if command.startswith("open "):
        app_name = command.replace("open ", "").strip()
        result = open_app(app_name)
        if result:
            return result

    # ── AI FALLBACK ──────────────────────────────────────────
    if is_detailed_request(command):
        return ask_ai(command + " Give a detailed explanation.")
    return ask_ai(command)