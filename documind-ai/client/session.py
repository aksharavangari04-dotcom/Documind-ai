import json
import os

SESSION_FILE = "session.json"


def save_session(data):
    with open(SESSION_FILE, "w") as file:
        json.dump(data, file, indent=4)


def load_session():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as file:
            return json.load(file)
    return None


def clear_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
