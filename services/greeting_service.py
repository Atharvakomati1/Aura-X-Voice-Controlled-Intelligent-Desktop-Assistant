from datetime import datetime
import requests
import os
from dotenv import load_dotenv
load_dotenv()

def get_greeting():
    now = datetime.now()
    hour = now.hour

    if hour < 12:
        return "Good morning"
    elif hour < 18:
        return "Good afternoon"
    else:
        return "Good evening"


from datetime import datetime

def number_to_words(n):
    words = {
        1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth",
        6: "sixth", 7: "seventh", 8: "eighth", 9: "ninth", 10: "tenth",
        11: "eleventh", 12: "twelfth", 13: "thirteenth", 14: "fourteenth",
        15: "fifteenth", 16: "sixteenth", 17: "seventeenth",
        18: "eighteenth", 19: "nineteenth", 20: "twentieth",
        21: "twenty-first", 22: "twenty-second", 23: "twenty-third",
        24: "twenty-fourth", 25: "twenty-fifth", 26: "twenty-sixth",
        27: "twenty-seventh", 28: "twenty-eighth", 29: "twenty-ninth",
        30: "thirtieth", 31: "thirty-first"
    }
    return words.get(n, str(n))


def get_date():
    now = datetime.now()
    day = now.strftime("%A")
    date_word = number_to_words(now.day)
    month = now.strftime("%B")

    from datetime import datetime

def number_to_words(n):
    words = {
        1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth",
        6: "sixth", 7: "seventh", 8: "eighth", 9: "ninth", 10: "tenth",
        11: "eleventh", 12: "twelfth", 13: "thirteenth", 14: "fourteenth",
        15: "fifteenth", 16: "sixteenth", 17: "seventeenth",
        18: "eighteenth", 19: "nineteenth", 20: "twentieth",
        21: "twenty-first", 22: "twenty-second", 23: "twenty-third",
        24: "twenty-fourth", 25: "twenty-fifth", 26: "twenty-sixth",
        27: "twenty-seventh", 28: "twenty-eighth", 29: "twenty-ninth",
        30: "thirtieth", 31: "thirty-first"
    }
    return words.get(n, str(n))


def get_date():
    now = datetime.now()
    day = now.strftime("%A")
    date_word = number_to_words(now.day)
    month = now.strftime("%B")

    from datetime import datetime

def number_to_words(n):
    words = {
        1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth",
        6: "sixth", 7: "seventh", 8: "eighth", 9: "ninth", 10: "tenth",
        11: "eleventh", 12: "twelfth", 13: "thirteenth", 14: "fourteenth",
        15: "fifteenth", 16: "sixteenth", 17: "seventeenth",
        18: "eighteenth", 19: "nineteenth", 20: "twentieth",
        21: "twenty-first", 22: "twenty-second", 23: "twenty-third",
        24: "twenty-fourth", 25: "twenty-fifth", 26: "twenty-sixth",
        27: "twenty-seventh", 28: "twenty-eighth", 29: "twenty-ninth",
        30: "thirtieth", 31: "thirty-first"
    }
    return words.get(n, str(n))


def get_date():
    now = datetime.now()
    day = now.strftime("%A")
    date_word = number_to_words(now.day)
    month = now.strftime("%B")

    from datetime import datetime

def number_to_words(n):
    words = {
        1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth",
        6: "sixth", 7: "seventh", 8: "eighth", 9: "ninth", 10: "tenth",
        11: "eleventh", 12: "twelfth", 13: "thirteenth", 14: "fourteenth",
        15: "fifteenth", 16: "sixteenth", 17: "seventeenth",
        18: "eighteenth", 19: "nineteenth", 20: "twentieth",
        21: "twenty-first", 22: "twenty-second", 23: "twenty-third",
        24: "twenty-fourth", 25: "twenty-fifth", 26: "twenty-sixth",
        27: "twenty-seventh", 28: "twenty-eighth", 29: "twenty-ninth",
        30: "thirtieth", 31: "thirty-first"
    }
    return words.get(n, str(n))


def get_date():
    now = datetime.now()
    day = now.strftime("%A")
    date_word = number_to_words(now.day)
    month = now.strftime("%B")

    return f"{day}, the {date_word} of {month}"

import requests

def get_weather():
    try:
        # 🌍 Get location from IP
        loc = requests.get("http://ip-api.com/json/", timeout=5).json()
        city = loc.get("city", "your city")

        # 🌤️ OpenWeatherMap API
        API_KEY = os.getenv("WEATHER_API_KEY")

        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

        data = requests.get(url, timeout=5).json()

        desc = data["weather"][0]["description"]
        temp = data["main"]["temp"]

        return f"Weather is {desc.lower()} today with temperature around {int(temp)}°C"

    except Exception:
        return "Weather is currently unavailable"


def generate_intro():
    greeting = get_greeting()
    date = get_date()
    weather = get_weather()

    return f"{greeting} Sir, Today is {date}, the {weather}\n,How may I assist you?"