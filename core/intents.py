def detect_intent(command: str) -> str:
    command = command.lower()

    if "time" in command:
        return "time"
    elif "youtube" in command:
        return "youtube"
    elif "open google" in command:
        return "google"
    elif "exit" in command or "shutdown" in command:
        return "exit"
    else:
        return "chat"