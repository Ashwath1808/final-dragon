# 🐉 DRAGON AI CORE 2.0 - Autonomous Desktop Companion

A sleek, next-generation Cyberpunk / Iron Man HUD desktop AI assistant built with **Python**, **Eel**, **HTML5/CSS3/JavaScript**, **pyttsx3**, **SpeechRecognition**, and **OpenCV**.

---

## ⚡ Key Highlights of Dragon 2.0

### 1. 🎨 Creative Cyberpunk HUD Interface
- **Holographic Arc Reactor Centerpiece**: Interactive animated multi-ring reactor that visualizes Dragon's brain state (`STANDBY`, `LISTENING`, `PROCESSING`, `SPEAKING`, `ALERT`).
- **Dynamic SiriWave Soundwave**: Soundwave reactive animation synchronized with Dragon's voice.
- **Click-to-Speak Core**: Clicking the center Arc Reactor or the Mic button instantly triggers voice listening.
- **Multi-Theme Switcher**:
  - 🔷 **Cyber Blue** (Electric Cyan & Deep Obsidian)
  - 🔴 **Crimson Dragon** (Fiery Hot Red & Dark Lava)
  - 🟢 **Matrix Emerald** (Digital Cyber Green)
  - 🟣 **Void Purple** (Ultraviolet & Royal Amethyst)
- **Real-Time HUD Header**: Digital Clock (HH:MM:SS), Date, and live status pill.
- **Slide-Out Drawers**:
  - **Conversation Logs Drawer**: Complete chat history with rich interactive cards (Weather, News, Wikipedia, Screenshots, Calculations, System diagnostics).
  - **Command Directory Hub**: Searchable categorized cards with 1-click command execution.
- **Interactive Modals**:
  - **System Telemetry HUD**: Live CPU load, RAM usage, Disk space, Battery status, and OS info.
  - **Settings & Config Panel**: Customize Assistant Name, Wake Word, Safe Word, Voice models, Speech rate/volume, API keys, and Emergency emails.
  - **Emergency SOS Fullscreen Overlay**: Flashing tactical alert with 5-second countdown and abort button.

---

## 🚀 How to Run

### Method 1: Double Click
Simply double-click `run_dragon.bat` in the project folder.

### Method 2: Command Line
```powershell
# Using the project's virtual environment
.\envDragon\Scripts\python.exe main.py
```

---

## 🎙️ Command Capabilities

Both **Voice** and **Keyboard Text Input** support all of the following commands:

### 🌐 Apps & Websites
| Command | What Dragon Does |
|---|---|
| `open notepad` / `calc` / `paint` | Launches native Windows desktop apps |
| `open vs code` / `open terminal` | Opens developer tools |
| `open task manager` / `open settings` | Opens system utilities |
| `open youtube` / `google` / `github` | Launches popular websites |
| `open reddit` / `spotify` / `netflix` | Opens entertainment platforms |

### 🧠 Knowledge & AI
| Command | What Dragon Does |
|---|---|
| `weather` or `weather in [city]` | Real-time weather, temperature, humidity, wind |
| `news` or `headlines` | Top 5 headlines with direct links |
| `who is [person]` / `what is [concept]` | 2-sentence Wikipedia summary with rich card |
| `what time is it` / `what date is today` | Current time and date |
| `calculate 250 * 4` / `15 percent of 80` | Evaluates math expressions |
| General questions | Smart contextual answering (or OpenAI GPT if API key provided) |

### 🖥️ Desktop & Hardware Controls
| Command | What Dragon Does |
|---|---|
| `take screenshot` | Captures full screen, saves to `www/screenshots/` and displays preview |
| `system status` / `diagnostics` | Shows live CPU %, RAM %, Disk %, and Battery % |
| `volume up` / `volume down` / `mute` | Adjusts master Windows volume |
| `lock computer` / `lock screen` | Safely locks your Windows workstation |

### 🎮 Fun & Entertainment
| Command | What Dragon Does |
|---|---|
| `play [song/artist] on youtube` | Auto-searches and plays on YouTube |
| `tell me a joke` | Tells clever programmer and tech jokes |
| `flip a coin` | Flips a coin (Heads or Tails) |
| `roll a dice` | Rolls a 6-sided die |

### 🚨 Emergency SOS System
| Trigger | Action |
|---|---|
| Say `"help me"` or `"red dragon"` or click SOS | Activates tactical emergency sequence with 5s cancel timer. If not aborted, captures live GPS coordinates and records 8s webcam video, then emails emergency contacts! |

---

## ⚙️ Configuration (`config.json`)

All settings are stored in `config.json` and can be edited either directly or through the **Settings Modal (Gear Icon)** in the UI:

```json
{
    "assistant_name": "Dragon",
    "wake_word": "dragon",
    "safe_word": "help me",
    "voice_index": 0,
    "speech_rate": 175,
    "speech_volume": 1.0,
    "tts_enabled": true,
    "auto_listen": false,
    "openai_api_key": "",
    "news_api_key": "7e6cbb87a9934eb0813db23e14c914c6",
    "email_sender": "ashwathalagond685@gmail.com",
    "email_password": "***************",
    "alert_recipients": [
        "ashwathalagond17@gmail.com",
        "aswathashu863@gmail.com"
    ],
    "theme": "cyber-blue"
}
```

---

## 💡 Keyboard Shortcuts
- **Enter**: Submit typed command.
- **Up / Down Arrow**: Cycle through command input history.
