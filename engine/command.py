import time
import threading
import queue
import smtplib
import pyttsx3
import speech_recognition as sr
import eel

from engine.config import load_config, save_config, get_system_voices
import engine.features as feat

# Thread-safe TTS Engine Lock & State
_tts_lock = threading.Lock()
_speech_queue = queue.Queue()
_is_speaking = False

# Background Listening Thread Controls
_listening_thread = None
_listening_active = False
_stop_listening_flag = threading.Event()


def speak(text, block=False):
    """Speaks the text using pyttsx3 and notifies frontend."""
    if not text:
        return

    # Notify UI
    try:
        eel.UpdateAssistantState("speaking", text)()
    except Exception as e:
        print("UI Notify Error:", e)

    def _speak_worker(msg):
        global _is_speaking
        with _tts_lock:
            _is_speaking = True
            try:
                config = load_config()
                if config.get("tts_enabled", True):
                    engine = pyttsx3.init()
                    voices = engine.getProperty('voices')
                    voice_idx = int(config.get("voice_index", 0))
                    if 0 <= voice_idx < len(voices):
                        engine.setProperty('voice', voices[voice_idx].id)
                    engine.setProperty('rate', int(config.get("speech_rate", 175)))
                    engine.setProperty('volume', float(config.get("speech_volume", 1.0)))
                    engine.say(msg)
                    engine.runAndWait()
                    engine.stop()
            except Exception as e:
                print("TTS Worker Error:", e)
            finally:
                _is_speaking = False
                try:
                    idle_state = "listening" if _listening_active else "idle"
                    eel.UpdateAssistantState(idle_state, "Ready for command")()
                except:
                    pass

    t = threading.Thread(target=_speak_worker, args=(text,), daemon=True)
    t.start()
    if block:
        t.join()


def takeCommandOnce(timeout=5, phrase_limit=7):
    """Listens for a single speech query."""
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Listening for speech...")
            try:
                eel.UpdateAssistantState("listening", "Listening to your voice...")()
            except:
                pass
            r.pause_threshold = 1.0
            r.adjust_for_ambient_noise(source, duration=0.8)
            audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)

        try:
            eel.UpdateAssistantState("processing", "Analyzing speech...")()
        except:
            pass

        text = r.recognize_google(audio, language='en')
        print("Recognized Speech:", text)
        return text.strip()
    except sr.WaitTimeoutError:
        print("Speech recognition timeout: No speech detected.")
        return ""
    except sr.UnknownValueError:
        print("Speech recognition could not understand audio.")
        return ""
    except Exception as e:
        print("Speech recognition error:", e)
        return ""
    finally:
        try:
            if not _is_speaking:
                idle_state = "listening" if _listening_active else "idle"
                eel.UpdateAssistantState(idle_state, "Ready for command")()
        except:
            pass


@eel.expose
def processCommand(query):
    """Processes any user command (from speech or web text input)."""
    if not query or not query.strip():
        return

    q = query.strip()
    q_lower = q.lower()
    config = load_config()
    safe_word = config.get("safe_word", "help me").lower()
    asst_name = config.get("assistant_name", "Dragon").lower()

    # Append user message to chat UI
    try:
        eel.AppendChatMessage("user", q, "text", {})()
    except Exception as e:
        print("Chat UI Error:", e)

    try:
        eel.UpdateAssistantState("processing", f"Executing: {q}")()
    except:
        pass

    # 1. EMERGENCY / SAFE WORD CHECK
    if safe_word in q_lower or "emergency" in q_lower or "red dragon" in q_lower:
        speak("Emergency protocol triggered. Stand by.")
        try:
            eel.TriggerEmergencyUI(5)()
        except Exception as e:
            print("Emergency UI Error:", e)
        feat.triggerEmergencyAlert()
        res_text = "🚨 EMERGENCY PROTOCOL ENGAGED! Live GPS coordinates and webcam recording dispatched to emergency contacts."
        try:
            eel.AppendChatMessage("dragon", res_text, "emergency", {})()
        except:
            pass
        return

    # 2. SCREENSHOT
    if "screenshot" in q_lower or "capture screen" in q_lower or "snapshot" in q_lower:
        res = feat.takeScreenshot()
        if res.get("success"):
            speak("Screenshot captured and displayed.")
            try:
                eel.AppendChatMessage("dragon", res["speech"], "screenshot", {"web_path": res["web_path"], "filename": res["filename"]})()
            except:
                pass
        else:
            speak(res["speech"])
            try:
                eel.AppendChatMessage("dragon", res["speech"], "text", {})()
            except:
                pass
        return

    # 3. SYSTEM DIAGNOSTICS
    if any(k in q_lower for k in ["system status", "diagnostics", "hardware", "cpu usage", "ram usage", "battery", "system health"]):
        stats = feat.getSystemDiagnostics()
        if stats.get("success"):
            speak(stats["speech"])
            try:
                eel.AppendChatMessage("dragon", f"System Diagnostics: CPU {stats['cpu_percent']}%, RAM {stats['memory_percent']}%, Battery {stats['battery_percent']}%", "system", stats)()
                eel.UpdateSystemHUD(stats)()
            except:
                pass
        else:
            speak(stats["speech"])
        return

    # 4. WEATHER
    if "weather" in q_lower or "temperature" in q_lower or "forecast" in q_lower:
        city = None
        m = re.search(r'(?:weather|temperature|forecast)\s+(?:in|for|at)?\s*([a-zA-Z\s]+)', q_lower)
        if m and m.group(1).strip() and not any(w in m.group(1).strip() for w in ["today", "now", "outside", "like"]):
            city = m.group(1).strip()
        weather = feat.fetchWeather(city)
        speak(weather["speech"])
        try:
            eel.AppendChatMessage("dragon", weather["speech"], "weather", weather)()
        except:
            pass
        return

    # 5. NEWS
    if "news" in q_lower or "headline" in q_lower:
        news_data = feat.fetchNews()
        speak(news_data["speech"])
        try:
            eel.AppendChatMessage("dragon", "Here are the latest top news headlines:", "news", news_data)()
        except:
            pass
        return

    # 6. WIKIPEDIA
    if any(k in q_lower for k in ["who is", "what is", "tell me about", "wikipedia", "explain"]) and not any(k in q_lower for k in ["time", "weather", "date", "your name"]):
        wiki = feat.fetchWikipedia(q)
        speak(wiki["speech"])
        try:
            card_type = "wikipedia" if wiki.get("success") else "text"
            eel.AppendChatMessage("dragon", wiki["speech"], card_type, wiki)()
        except:
            pass
        return

    # 7. TIME & DATE
    if any(k in q_lower for k in ["what time", "current time", "what is the time", "what date", "today's date", "what day"]):
        dt = feat.getDateTime()
        speak(dt["speech"])
        try:
            eel.AppendChatMessage("dragon", dt["speech"], "text", {})()
        except:
            pass
        return

    # 8. VOLUME CONTROLS
    if "volume" in q_lower or "mute" in q_lower or "unmute" in q_lower:
        vol = feat.changeVolume(q_lower)
        speak(vol["speech"])
        try:
            eel.AppendChatMessage("dragon", vol["speech"], "text", {})()
        except:
            pass
        return

    # 9. LOCK COMPUTER
    if "lock computer" in q_lower or "lock screen" in q_lower or "lock pc" in q_lower or "lock workstation" in q_lower:
        speak("Locking your workstation now.")
        try:
            eel.AppendChatMessage("dragon", "Workstation locked.", "text", {})()
        except:
            pass
        feat.lockWorkstation()
        return

    # 10. JOKES, COIN, DICE
    if "joke" in q_lower or "make me laugh" in q_lower:
        j = feat.tellJoke()
        speak(j["speech"])
        try:
            eel.AppendChatMessage("dragon", j["joke"], "joke", {})()
        except:
            pass
        return

    if "flip a coin" in q_lower or "coin flip" in q_lower or "toss a coin" in q_lower:
        c = feat.flipCoin()
        speak(c["speech"])
        try:
            eel.AppendChatMessage("dragon", f"🪙 Result: {c['outcome']}", "text", {})()
        except:
            pass
        return

    if "roll a dice" in q_lower or "roll dice" in q_lower or "roll a die" in q_lower:
        d = feat.rollDice()
        speak(d["speech"])
        try:
            eel.AppendChatMessage("dragon", f"🎲 You rolled: {d['roll']}", "text", {})()
        except:
            pass
        return

    # 11. YOUTUBE PLAYBACK
    if "play" in q_lower and ("youtube" in q_lower or "song" in q_lower or "music" in q_lower or "video" in q_lower):
        res = feat.playYoutube(q)
        speak(res["message"])
        try:
            eel.AppendChatMessage("dragon", res["message"], "youtube", res)()
        except:
            pass
        return

    # 12. APP & WEB LAUNCHER
    if "open" in q_lower or "launch" in q_lower or "start" in q_lower:
        res = feat.openAppOrWeb(q)
        speak(res.get("message", "Opening request"))
        try:
            eel.AppendChatMessage("dragon", res.get("message", "Opening request"), "text", res)()
        except:
            pass
        return

    # 13. MATH / CALCULATION
    if any(k in q_lower for k in ["calculate", "math", "solve", "+", "*", "/", "percent of", "% of", "divided by", "multiplied by"]):
        m_res = feat.calculateMath(q)
        if m_res.get("success"):
            speak(m_res["speech"])
            try:
                eel.AppendChatMessage("dragon", f"Calculation: {m_res['expression']} = {m_res['result']}", "math", m_res)()
            except:
                pass
            return

    # 14. GOOGLE SEARCH
    if q_lower.startswith("search") or q_lower.startswith("google"):
        s_res = feat.googleSearch(q)
        speak(s_res["message"])
        try:
            eel.AppendChatMessage("dragon", s_res["message"], "search", s_res)()
        except:
            pass
        return

    # 15. GENERAL CONVERSATION / OPENAI FALLBACK
    ai_res = feat.askAI(q)
    speak(ai_res["speech"])
    try:
        eel.AppendChatMessage("dragon", ai_res["answer"], "ai", ai_res)()
    except:
        pass


@eel.expose
def startSingleListen():
    """Triggered when the user clicks the Mic button in the UI."""
    def _listen_worker():
        feat.playClickSound()
        spoken_text = takeCommandOnce(timeout=5, phrase_limit=7)
        if spoken_text:
            processCommand(spoken_text)
        else:
            try:
                eel.UpdateAssistantState("idle", "No speech detected.")()
            except:
                pass

    threading.Thread(target=_listen_worker, daemon=True).start()


def _continuous_listening_loop():
    """Background continuous listener loop."""
    global _listening_active
    print("Continuous listening thread started.")
    config = load_config()
    wake_word = config.get("wake_word", "dragon").lower()
    safe_word = config.get("safe_word", "help me").lower()

    while not _stop_listening_flag.is_set():
        if _is_speaking:
            time.sleep(0.5)
            continue

        try:
            query = takeCommandOnce(timeout=4, phrase_limit=6)
            if not query:
                time.sleep(0.2)
                continue

            q_low = query.lower()
            # If safe word triggered directly
            if safe_word in q_low or "emergency" in q_low:
                processCommand(query)
                continue

            # If wake word is spoken or already addressed
            if wake_word in q_low:
                clean_query = q_low.replace(wake_word, "").strip()
                if clean_query:
                    processCommand(clean_query)
                else:
                    speak("Yes, I am listening. How can I assist you?")
            else:
                # If continuous mode is actively on and query was spoken
                if len(query.split()) > 1:
                    processCommand(query)

        except Exception as e:
            print("Listening loop error:", e)
            time.sleep(1)

    _listening_active = False
    print("Continuous listening thread stopped.")


@eel.expose
def toggleAutoListen(enable):
    """Enables or disables continuous background listening."""
    global _listening_thread, _listening_active

    if enable:
        if not _listening_active:
            _stop_listening_flag.clear()
            _listening_active = True
            _listening_thread = threading.Thread(target=_continuous_listening_loop, daemon=True)
            _listening_thread.start()
            try:
                eel.UpdateAssistantState("listening", "Voice listening active.")()
            except:
                pass
            return {"active": True}
    else:
        if _listening_active:
            _stop_listening_flag.set()
            _listening_active = False
            try:
                eel.UpdateAssistantState("idle", "Voice listening paused.")()
            except:
                pass
            return {"active": False}

    return {"active": _listening_active}


@eel.expose
def getLiveSystemStats():
    """Returns telemetry data to the frontend."""
    return feat.getSystemDiagnostics()


@eel.expose
def getAppConfig():
    """Returns current configuration."""
    return load_config()


@eel.expose
def saveAppConfig(new_config):
    """Saves new configuration received from settings modal."""
    success = save_config(new_config)
    if success:
        return {"success": True, "message": "Settings updated successfully."}
    return {"success": False, "message": "Failed to save settings."}


@eel.expose
def getVoiceList():
    """Returns available TTS voices on the machine."""
    return get_system_voices()


@eel.expose
def triggerEmergencySOS():
    """UI button trigger for emergency alert."""
    feat.triggerEmergencyAlert()
    return {"triggered": True}


@eel.expose
def cancelEmergencySOS():
    """UI cancel button for emergency alert."""
    return feat.cancelEmergencyAlert()


@eel.expose
def testEmailCredentials(sender_email, sender_pass):
    """Tests Gmail SMTP connection and credentials directly."""
    try:
        clean_email = (sender_email or "").strip()
        clean_pass = (sender_pass or "").replace(" ", "").strip()
        if not clean_email or not clean_pass:
            return {"success": False, "message": "Email and password cannot be empty."}

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
            server.login(clean_email, clean_pass)
        return {"success": True, "message": "Connection & App Password verified successfully!"}
    except smtplib.SMTPAuthenticationError as e:
        return {
            "success": False,
            "message": "Authentication failed (535): Invalid username or App Password. Check 2FA & App Passwords in your Google Account."
        }
    except Exception as e:
        return {"success": False, "message": f"Connection error: {str(e)}"}


@eel.expose
def quickAction(action_id):
    """Direct execution for quick action chips."""
    feat.playClickSound()
    if action_id == "weather":
        processCommand("weather")
    elif action_id == "news":
        processCommand("news")
    elif action_id == "system":
        processCommand("system status")
    elif action_id == "screenshot":
        processCommand("take screenshot")
    elif action_id == "joke":
        processCommand("tell me a joke")
    elif action_id == "dice":
        processCommand("roll a dice")
    elif action_id == "time":
        processCommand("what time is it")
    elif action_id == "emergency":
        processCommand("help me")
    elif action_id == "calc":
        processCommand("calculate 125 * 8")
    else:
        processCommand(action_id)
    return {"status": "ok"}
