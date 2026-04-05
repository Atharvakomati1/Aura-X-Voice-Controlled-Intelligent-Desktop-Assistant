import speech_recognition as sr

def listen(verbose=True):
    r = sr.Recognizer()

    # 🔥 tuned values (balanced)
    r.energy_threshold = 300
    r.dynamic_energy_threshold = True
    r.pause_threshold = 1.8
    r.phrase_threshold = 0.3

    with sr.Microphone() as source:
        if verbose:
            print("🎤 Calibrating...")

        r.adjust_for_ambient_noise(source, duration=1)

        if verbose:
            print("🎤 Speak now...")

            try:
                audio = r.listen(
                    source,
                    timeout=10,
                    phrase_time_limit=15
                )

                if verbose:
                    print("🔍 Recognizing...")

                text = r.recognize_google(audio, language="en-IN")

                if verbose:
                    print("✅ You said:", text)

                return text.lower()

            except sr.UnknownValueError:
                if verbose:
                    print("❌ Could not understand")
                return ""

            except sr.WaitTimeoutError:
                if verbose:
                    print("⏱️ Timeout")
                return ""
            except Exception as e:
                print("Error:", e)
                return ""
