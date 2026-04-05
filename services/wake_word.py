import speech_recognition as sr

def detect_wake_word():
    r = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        r.adjust_for_ambient_noise(source)

    try:
        with mic as source:
            audio = r.listen(source, timeout=3, phrase_time_limit=3)

        text = r.recognize_google(audio).lower()

        if "hey aura" in text or "hello aura" in text:
            return True

    except:
        pass

    return False