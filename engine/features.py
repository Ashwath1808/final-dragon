import os
import re
import smtplib
import time
import datetime
import random
import threading
import webbrowser
import platform
import ctypes
from email.message import EmailMessage

import cv2
import geocoder
import requests
import wikipedia
import pyautogui
import psutil
from playsound import playsound

from engine.config import load_config, save_config, CURRENT_CONFIG

# Ensure screenshots directory exists
SCREENSHOT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "www", "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# ----------------- SOUND PLAYER -----------------
def playAssistantSound(sound_type="click"):
    """Plays audio notification asynchronously to prevent blocking."""
    def _play():
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if sound_type == "click":
                sound_path = os.path.join(base_dir, "www", "assets", "audio", "mouse-click.mp3")
            elif sound_type == "startup":
                sound_path = os.path.join(base_dir, "www", "assets", "audio", "myinstants.mp3")
            else:
                sound_path = os.path.join(base_dir, "www", "assets", "audio", "mouse-click.mp3")

            if os.path.exists(sound_path):
                playsound(sound_path)
        except Exception as e:
            print("Sound error:", e)

    threading.Thread(target=_play, daemon=True).start()

def playClickSound():
    playAssistantSound("click")

def playAssistentSound():
    playAssistantSound("startup")


# ----------------- APP & WEB LAUNCHER -----------------
APP_MAP = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "calc": "calc.exe",
    "paint": "mspaint.exe",
    "command prompt": "cmd.exe",
    "cmd": "cmd.exe",
    "terminal": "powershell.exe",
    "powershell": "powershell.exe",
    "task manager": "taskmgr.exe",
    "file explorer": "explorer.exe",
    "explorer": "explorer.exe",
    "camera": "start microsoft.windows.camera:",
    "settings": "start ms-settings:",
    "code": "code",
    "vs code": "code",
    "visual studio code": "code",
    "chrome": "chrome.exe",
    "edge": "msedge.exe",
    "spotify": "spotify.exe"
}

WEB_MAP = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "github": "https://github.com",
    "reddit": "https://reddit.com",
    "twitter": "https://x.com",
    "x": "https://x.com",
    "instagram": "https://instagram.com",
    "linkedin": "https://linkedin.com",
    "whatsapp": "https://web.whatsapp.com",
    "netflix": "https://netflix.com",
    "spotify": "https://open.spotify.com",
    "chatgpt": "https://chatgpt.com",
    "amazon": "https://amazon.com",
    "discord": "https://discord.com",
    "gmail": "https://mail.google.com",
    "wikipedia": "https://wikipedia.org",
    "stackoverflow": "https://stackoverflow.com",
    "twitch": "https://twitch.tv"
}

def openAppOrWeb(query):
    """Opens either a desktop application or a website."""
    q = query.lower().strip()
    config = load_config()
    asst_name = config.get("assistant_name", "Dragon").lower()
    q = q.replace(asst_name, "").replace("open", "").replace("launch", "").strip()

    # Check for direct website match
    for site, url in WEB_MAP.items():
        if site in q:
            webbrowser.open(url)
            return {"type": "web", "success": True, "target": site.capitalize(), "url": url, "message": f"Opening {site.capitalize()}"}

    # Check for desktop app match
    for app_name, app_cmd in APP_MAP.items():
        if app_name in q:
            try:
                os.system(f"start {app_cmd}")
                return {"type": "app", "success": True, "target": app_name.capitalize(), "message": f"Launching {app_name.capitalize()}"}
            except Exception as e:
                return {"type": "app", "success": False, "target": app_name, "message": f"Failed to open {app_name}: {e}"}

    # Check for general domain (.com, .org, etc.)
    if re.search(r'\.(com|org|net|io|co|in|edu|gov)$', q) or q.startswith("http"):
        url = q if q.startswith("http") else f"https://{q}"
        webbrowser.open(url)
        return {"type": "web", "success": True, "target": q, "url": url, "message": f"Opening {q}"}

    # Fallback: treat as Google search
    return googleSearch(q)


# ----------------- YOUTUBE & SEARCH -----------------
def extract_yt_term(command):
    patterns = [
        r'play\s+(.*?)\s+on\s+youtube',
        r'play\s+(.*?)\s+in\s+youtube',
        r'play\s+(.*)',
        r'youtube\s+(.*)'
    ]
    for p in patterns:
        m = re.search(p, command, re.IGNORECASE)
        if m and m.group(1).strip():
            return m.group(1).strip()
    return command.replace("play", "").replace("youtube", "").strip()

def playYoutube(query):
    """Searches and plays a video/song on YouTube."""
    term = extract_yt_term(query)
    if not term:
        term = "top trending music"
    try:
        import pywhatkit as kit
        kit.playonyt(term)
        return {"success": True, "query": term, "message": f"Playing {term} on YouTube"}
    except Exception as e:
        url = f"https://www.youtube.com/results?search_query={term.replace(' ', '+')}"
        webbrowser.open(url)
        return {"success": True, "query": term, "url": url, "message": f"Opening YouTube search for {term}"}

def googleSearch(query):
    """Searches Google for query."""
    config = load_config()
    asst_name = config.get("assistant_name", "Dragon").lower()
    clean_q = query.lower().replace(asst_name, "").replace("search", "").replace("google", "").strip()
    if not clean_q:
        clean_q = query.strip()
    search_url = f"https://www.google.com/search?q={clean_q.replace(' ', '+')}"
    webbrowser.open(search_url)
    return {"type": "search", "query": clean_q, "url": search_url, "message": f"Searching Google for {clean_q}"}


# ----------------- NEWS FETCHER -----------------
def fetchNews():
    """Fetches top 5 headlines."""
    config = load_config()
    api_key = config.get("news_api_key", "7e6cbb87a9934eb0813db23e14c914c6")
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"

    try:
        r = requests.get(url, timeout=6)
        if r.status_code == 200:
            data = r.json()
            raw_articles = data.get('articles', [])
            articles = []
            for art in raw_articles[:5]:
                title = art.get('title', 'No Title')
                desc = art.get('description', '') or 'Read full story on the original source.'
                source = art.get('source', {}).get('name', 'News')
                art_url = art.get('url', '#')
                articles.append({
                    "title": title,
                    "description": desc,
                    "source": source,
                    "url": art_url
                })
            spoken = "Here are today's top headlines: " + ". ".join([a["title"] for a in articles[:3]])
            return {"success": True, "articles": articles, "speech": spoken}
    except Exception as e:
        print("NewsAPI error:", e)

    # Fallback to general tech news feed if API fails
    fallback_articles = [
        {"title": "Global Tech & AI Innovations Advance Rapidly", "description": "Breakthrough developments in artificial intelligence and automation reshape digital landscape.", "source": "TechDaily", "url": "https://news.google.com"},
        {"title": "Space Exploration Programs Gear Up for Next Missions", "description": "International agencies announce new lunar and orbital objectives.", "source": "ScienceWire", "url": "https://news.google.com"},
        {"title": "Renewable Energy Adoption Reaches Record High", "description": "Solar and wind generation continue to surpass previous annual projections.", "source": "EcoNews", "url": "https://news.google.com"}
    ]
    return {
        "success": True,
        "articles": fallback_articles,
        "speech": "Here are today's top headlines: Global Tech Innovations Advance, Space Programs Gear Up, and Renewable Energy reaches Record High."
    }


# ----------------- WEATHER -----------------
def fetchWeather(city=None):
    """Fetches real-time weather using wttr.in (clean, JSON, zero-config)."""
    try:
        location_str = city.strip() if city else ""
        url = f"https://wttr.in/{location_str}?format=j1"
        r = requests.get(url, timeout=6)
        if r.status_code == 200:
            data = r.json()
            current = data['current_condition'][0]
            temp_c = current['temp_C']
            temp_f = current['temp_F']
            feels_c = current['FeelsLikeC']
            desc = current['weatherDesc'][0]['value']
            humidity = current['humidity']
            wind = current['windspeedKmph']

            nearest_area = data.get('nearest_area', [{}])[0]
            area_name = nearest_area.get('areaName', [{}])[0].get('value', city or 'Local Area')
            country = nearest_area.get('country', [{}])[0].get('value', '')

            speech = f"Current weather in {area_name} is {desc} with a temperature of {temp_c} degrees Celsius, humidity at {humidity} percent."
            return {
                "success": True,
                "city": area_name,
                "country": country,
                "temp_c": temp_c,
                "temp_f": temp_f,
                "feels_c": feels_c,
                "condition": desc,
                "humidity": humidity,
                "wind_kmph": wind,
                "speech": speech
            }
    except Exception as e:
        print("Weather error:", e)

    return {
        "success": False,
        "city": city or "Unknown",
        "temp_c": "--",
        "condition": "Clear",
        "speech": "Sorry, I was unable to retrieve live weather data right now."
    }


# ----------------- WIKIPEDIA -----------------
def fetchWikipedia(query):
    """Fetches concise Wikipedia knowledge summary."""
    clean_q = query.lower()
    for word in ["who is", "what is", "tell me about", "wikipedia", "explain", "search wikipedia for"]:
        clean_q = clean_q.replace(word, "")
    clean_q = clean_q.strip()

    if not clean_q:
        return {"success": False, "speech": "What topic would you like me to look up on Wikipedia?"}

    try:
        # Search page first to get best match
        search_results = wikipedia.search(clean_q)
        if not search_results:
            return {"success": False, "speech": f"Sorry, I couldn't find any Wikipedia article on {clean_q}."}

        target_title = search_results[0]
        page = wikipedia.page(target_title, auto_suggest=False)
        summary = wikipedia.summary(target_title, sentences=2, auto_suggest=False)

        speech = f"According to Wikipedia: {summary}"
        return {
            "success": True,
            "title": page.title,
            "summary": summary,
            "url": page.url,
            "speech": speech
        }
    except wikipedia.DisambiguationError as e:
        try:
            target_title = e.options[0]
            summary = wikipedia.summary(target_title, sentences=2)
            return {
                "success": True,
                "title": target_title,
                "summary": summary,
                "url": f"https://en.wikipedia.org/wiki/{target_title.replace(' ', '_')}",
                "speech": f"According to Wikipedia: {summary}"
            }
        except:
            pass
    except Exception as e:
        print("Wikipedia error:", e)

    return {"success": False, "speech": f"I couldn't find detailed information about {clean_q}."}


# ----------------- SYSTEM CONTROLS & MONITOR -----------------
def takeScreenshot():
    """Takes a full screen capture and saves it to www/screenshots."""
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        filepath = os.path.join(SCREENSHOT_DIR, filename)
        web_path = f"screenshots/{filename}"

        img = pyautogui.screenshot()
        img.save(filepath)

        return {
            "success": True,
            "filename": filename,
            "web_path": web_path,
            "abs_path": filepath,
            "speech": "Screenshot captured and saved successfully."
        }
    except Exception as e:
        print("Screenshot error:", e)
        return {"success": False, "speech": f"Failed to capture screenshot: {e}"}

def changeVolume(action):
    """Adjusts Windows master volume using PyAutoGUI keys."""
    try:
        action = action.lower()
        if "up" in action or "raise" in action or "increase" in action:
            for _ in range(5):
                pyautogui.press('volumeup')
            return {"success": True, "speech": "Volume increased."}
        elif "down" in action or "lower" in action or "decrease" in action:
            for _ in range(5):
                pyautogui.press('volumedown')
            return {"success": True, "speech": "Volume decreased."}
        elif "mute" in action:
            pyautogui.press('volumemute')
            return {"success": True, "speech": "Volume muted."}
        elif "unmute" in action:
            pyautogui.press('volumemute')
            return {"success": True, "speech": "Volume unmuted."}
        elif "max" in action:
            for _ in range(25):
                pyautogui.press('volumeup')
            return {"success": True, "speech": "Volume set to maximum."}
    except Exception as e:
        print("Volume error:", e)
    return {"success": False, "speech": "Unable to modify volume."}

def lockWorkstation():
    """Locks the Windows computer."""
    try:
        ctypes.windll.user32.LockWorkStation()
        return {"success": True, "speech": "Locking workstation now."}
    except Exception as e:
        return {"success": False, "speech": f"Could not lock workstation: {e}"}

def getSystemDiagnostics():
    """Returns real-time hardware telemetry."""
    try:
        cpu_pct = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        mem_pct = mem.percent
        mem_used_gb = round(mem.used / (1024 ** 3), 2)
        mem_total_gb = round(mem.total / (1024 ** 3), 2)

        disk = psutil.disk_usage('C:')
        disk_pct = disk.percent
        disk_free_gb = round(disk.free / (1024 ** 3), 1)

        battery = psutil.sensors_battery()
        bat_pct = battery.percent if battery else 100
        bat_plugged = battery.power_plugged if battery else True

        # Uptime
        boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
        uptime_delta = datetime.datetime.now() - boot_time
        uptime_hours = round(uptime_delta.total_seconds() / 3600, 1)

        os_info = f"{platform.system()} {platform.release()}"
        hostname = platform.node()

        speech = f"System status: CPU usage is {cpu_pct} percent, memory usage is {mem_pct} percent with {mem_used_gb} gigabytes used of {mem_total_gb} gigabytes."
        if battery:
            speech += f" Battery is at {bat_pct} percent and {'plugged in' if bat_plugged else 'running on battery'}."

        return {
            "success": True,
            "cpu_percent": cpu_pct,
            "memory_percent": mem_pct,
            "memory_used_gb": mem_used_gb,
            "memory_total_gb": mem_total_gb,
            "disk_percent": disk_pct,
            "disk_free_gb": disk_free_gb,
            "battery_percent": bat_pct,
            "battery_plugged": bat_plugged,
            "uptime_hours": uptime_hours,
            "os": os_info,
            "hostname": hostname,
            "speech": speech
        }
    except Exception as e:
        print("System stats error:", e)
        return {"success": False, "speech": "Unable to read system telemetry."}


# ----------------- MATH & CALCULATOR -----------------
def calculateMath(query):
    """Safe basic calculation evaluator."""
    clean_q = query.lower()
    for word in ["calculate", "what is", "solve", "math", "evaluate"]:
        clean_q = clean_q.replace(word, "")
    clean_q = clean_q.replace("x", "*").replace("times", "*").replace("multiplied by", "*")
    clean_q = clean_q.replace("divided by", "/").replace("over", "/")
    clean_q = clean_q.replace("plus", "+").replace("minus", "-")
    clean_q = clean_q.replace("percent of", "* 0.01 *").replace("% of", "* 0.01 *")
    clean_q = clean_q.replace("^", "**")

    # Filter only safe characters
    allowed = set("0123456789+-*/(). %")
    expr = "".join([c for c in clean_q if c in allowed or c == '*']).strip()

    if not expr:
        return {"success": False, "speech": "Please specify a mathematical calculation."}

    try:
        # Safe eval of math expression
        result = eval(expr, {"__builtins__": {}}, {})
        result_formatted = f"{result:,}" if isinstance(result, (int, float)) and abs(result) >= 1000 else f"{result}"
        return {
            "success": True,
            "expression": expr,
            "result": result_formatted,
            "speech": f"The answer is {result_formatted}"
        }
    except Exception as e:
        return {"success": False, "speech": "I couldn't calculate that math expression."}


# ----------------- FUN & UTILITIES -----------------
JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs!",
    "Why did the developer go broke? Because he used up all his cache!",
    "There are 10 types of people in the world: those who understand binary, and those who don't.",
    "Why was the computer cold? It left its Windows open!",
    "An SQL statement walks into a bar, approaches two tables and asks: Can I join you?",
    "A programmer's wife tells him: Go to the store and get a loaf of bread. If they have eggs, get a dozen. He comes home with 12 loaves of bread.",
    "Hardware is the part of a computer you can kick; Software is the part you can only curse at.",
    "Why do Java programmers wear glasses? Because they don't C sharp!"
]

def tellJoke():
    joke = random.choice(JOKES)
    return {"success": True, "joke": joke, "speech": joke}

def flipCoin():
    outcome = random.choice(["Heads", "Tails"])
    return {"success": True, "outcome": outcome, "speech": f"It landed on {outcome}!"}

def rollDice(sides=6):
    roll = random.randint(1, sides)
    return {"success": True, "roll": roll, "speech": f"You rolled a {roll}!"}

def getDateTime():
    now = datetime.datetime.now()
    time_str = now.strftime("%I:%M %p")
    date_str = now.strftime("%A, %B %d, %Y")
    speech = f"Current time is {time_str}, today is {date_str}."
    return {"success": True, "time": time_str, "date": date_str, "speech": speech}


# ----------------- OPENAI / SMART CONVERSATION -----------------
def askAI(query):
    """Conversational fallback using OpenAI if configured, or smart built-in answers."""
    config = load_config()
    api_key = config.get("openai_api_key", "").strip()

    if api_key:
        try:
            import openai
            openai.api_key = api_key
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are Dragon, a sleek sci-fi AI assistant. Keep responses helpful, witty, and concise within 2-3 sentences."},
                    {"role": "user", "content": query}
                ],
                max_tokens=150,
                temperature=0.7
            )
            ans = response.choices[0].message['content'].strip()
            return {"success": True, "source": "OpenAI", "answer": ans, "speech": ans}
        except Exception as e:
            print("OpenAI error:", e)

    # Built-in contextual responses
    q = query.lower()
    if "who are you" in q or "what are you" in q:
        ans = "I am Dragon, your next-generation autonomous AI desktop companion, equipped with voice recognition, system controls, and real-time intelligence."
    elif "how are you" in q:
        ans = "All core systems operating at 100% capacity. Ready for your command!"
    elif "who made you" in q or "who created you" in q:
        ans = "I was engineered by my master creator to deliver high-performance autonomous assistance."
    elif "thank you" in q or "thanks" in q:
        ans = "You're very welcome! Always at your service."
    elif "hello" in q or "hi" in q or "hey" in q:
        ans = "Greetings! Dragon AI Core is online and listening. What can I do for you today?"
    elif "bye" in q or "goodbye" in q or "sleep" in q:
        ans = "Standing by in sleep mode. Call me whenever you need me."
    else:
        ans = f"I've noted that. Would you like me to search Google or Wikipedia for '{query}'?"

    return {"success": True, "source": "DragonCore", "answer": ans, "speech": ans}


# ----------------- EMERGENCY ALERT SYSTEM -----------------
_EMERGENCY_CANCELLED = False

def cancelEmergencyAlert():
    global _EMERGENCY_CANCELLED
    _EMERGENCY_CANCELLED = True
    print("Emergency alert cancelled by user.")
    return {"cancelled": True, "speech": "Emergency protocol aborted."}

def send_alert_email_process():
    """Background process for capturing location, video, and sending emergency email."""
    global _EMERGENCY_CANCELLED
    _EMERGENCY_CANCELLED = False

    config = load_config()
    sender_email = config.get("email_sender", "ashwathalagond685@gmail.com").strip()
    sender_pass = config.get("email_password", "").replace(" ", "").strip()
    recipients = config.get("alert_recipients", ["ashwathalagond17@gmail.com"])
    if isinstance(recipients, str):
        recipients = [r.strip() for r in recipients.split(",") if r.strip()]

    try:
        # 1. Live location
        g = geocoder.ip('me')
        lat = g.latlng[0] if g and g.latlng else 0.0
        lng = g.latlng[1] if g and g.latlng else 0.0
        loc_link = f"https://maps.google.com/?q={lat},{lng}"
        city_name = g.city if g and hasattr(g, 'city') and g.city else "Current Location"

        # 2. Record 8 seconds of webcam video
        video_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "alert_video.mp4")
        cap = cv2.VideoCapture(0)

        if cap.isOpened():
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            out = cv2.VideoWriter(video_file, fourcc, 20.0, (640, 480))
            start_t = time.time()
            while int(time.time() - start_t) < 8:
                if _EMERGENCY_CANCELLED:
                    cap.release()
                    out.release()
                    return {"success": False, "cancelled": True}
                ret, frame = cap.read()
                if ret:
                    out.write(frame)
                else:
                    break
            cap.release()
            out.release()

        if _EMERGENCY_CANCELLED:
            return {"success": False, "cancelled": True}

        # 3. Construct email
        msg = EmailMessage()
        msg["Subject"] = "🚨 CRITICAL EMERGENCY ALERT – Location + Video"
        msg["From"] = sender_email
        msg["To"] = ", ".join(recipients) if isinstance(recipients, list) else recipients

        msg.set_content(
            f"EMERGENCY ALERT TRIGGERED VIA DRAGON CORE!\n\n"
            f"📍 Approximate Location: {city_name}\n"
            f"🌐 Live Maps: {loc_link}\n"
            f"🕒 Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"📹 8-second emergency webcam recording is attached."
        )

        if os.path.exists(video_file):
            with open(video_file, "rb") as f:
                video_data = f.read()
                msg.add_attachment(video_data, maintype="video", subtype="mp4", filename="alert_video.mp4")

        # 4. Dispatch via SMTP
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as server:
            server.login(sender_email, sender_pass)
            server.send_message(msg)

        print("Emergency alert email successfully sent to:", recipients)
        try:
            import eel
            recip_str = ", ".join(recipients) if isinstance(recipients, list) else recipients
            eel.AppendChatMessage("dragon", f"✅ Emergency alert email successfully delivered to: {recip_str}", "text", {})()
        except Exception:
            pass
        return {"success": True, "location": loc_link, "lat": lat, "lng": lng}
    except smtplib.SMTPAuthenticationError as auth_err:
        print("Emergency dispatch authentication error:", auth_err)
        try:
            import eel
            eel.AppendChatMessage(
                "dragon",
                "❌ Emergency Email Failed: Gmail rejected the username or App Password (BadCredentials). Please generate a new 16-character App Password at myaccount.google.com/apppasswords and save it in Settings.",
                "text",
                {}
            )()
        except Exception:
            pass
        return {"success": False, "error": str(auth_err)}
    except Exception as e:
        print("Emergency dispatch error:", e)
        try:
            import eel
            eel.AppendChatMessage("dragon", f"❌ Emergency email dispatch error: {e}", "text", {})()
        except Exception:
            pass
        return {"success": False, "error": str(e)}

def triggerEmergencyAlert():
    """Starts emergency alert background thread."""
    t = threading.Thread(target=send_alert_email_process, daemon=True)
    t.start()
    return {"triggered": True, "speech": "Emergency alert sequence initiated. Location tracking and video capture engaged."}