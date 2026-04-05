import datetime

def get_time():
    return datetime.datetime.now().strftime("Current time is %H:%M")