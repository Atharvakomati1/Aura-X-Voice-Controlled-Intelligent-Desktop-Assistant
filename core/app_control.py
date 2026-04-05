import os

def find_app(app_name):
    app_name = app_name.lower()

    start_menu_paths = [
        os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"),
        os.path.expandvars(r"%PROGRAMDATA%\Microsoft\Windows\Start Menu\Programs")
    ]

    for path in start_menu_paths:
        for root, dirs, files in os.walk(path):
            for file in files:
                if app_name in file.lower() and file.endswith(".lnk"):
                    return os.path.join(root, file)

    return None

import subprocess

def open_app(app_name):
    app_path = find_app(app_name)

    if app_path:
        subprocess.Popen(app_path, shell=True)
        return f"Opening {app_name}"
    else:
        return None