import os
import json
import pyttsx3

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")

DEFAULT_CONFIG = {
    "assistant_name": "Dragon",
    "wake_word": "dragon",
    "safe_word": "help me",
    "voice_index": 0,
    "speech_rate": 175,
    "speech_volume": 1.0,
    "tts_enabled": True,
    "auto_listen": False,
    "openai_api_key": "",
    "news_api_key": "7e6cbb87a9934eb0813db23e14c914c6",
    "email_sender": "ashwathalagond685@gmail.com",
    "email_password": "lnqi oiov qwsq pyym",
    "alert_recipients": ["ashwathalagond17@gmail.com", "aswathashu863@gmail.com"],
    "theme": "cyber-blue",
    "browser": "edge"
}

def load_config():
    """Loads configuration from config.json or initializes it with defaults."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                config = {**DEFAULT_CONFIG, **data}
                return config
        except Exception as e:
            print("Error reading config.json, using defaults:", e)
    save_config(DEFAULT_CONFIG)
    return DEFAULT_CONFIG.copy()

def save_config(config_dict):
    """Saves configuration to config.json."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_dict, f, indent=4)
        return True
    except Exception as e:
        print("Error saving config.json:", e)
        return False

def get_system_voices():
    """Returns a list of all installed system voices with ID and Name."""
    voice_list = []
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        for i, v in enumerate(voices):
            voice_list.append({
                "index": i,
                "name": v.name,
                "id": v.id
            })
        engine.stop()
    except Exception as e:
        print("Error enumerating voices:", e)
    return voice_list

# Load initial config
CURRENT_CONFIG = load_config()
ASSISTANT_NAME = CURRENT_CONFIG.get("assistant_name", "Dragon")
WAKE_WORD = CURRENT_CONFIG.get("wake_word", "dragon").lower()
SAFE_WORD = CURRENT_CONFIG.get("safe_word", "help me").lower()