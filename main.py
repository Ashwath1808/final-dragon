import os
import sys
import time
import socket
import threading
import webbrowser
import eel
from engine.config import load_config
from engine.features import playAssistantSound
import engine.command as cmd

# Configure stdout and stderr with UTF-8 / replace errors and line buffering for Windows consoles
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
        sys.stderr.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass


def find_available_port(start_port=8000, max_attempts=50):
    """Finds an available TCP port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                return port
            except OSError:
                continue
    return start_port


def start_watchdog(port, timeout=6):
    """Background watchdog: ensures the user gets a working browser window even if app mode fails."""
    def _watch():
        time.sleep(timeout)
        if not getattr(eel, '_websockets', None):
            print(f"\n[!] Notice: No browser connection detected after {timeout}s.")
            print(f"[+] Opening in your default browser: http://localhost:{port}/index.html")
            try:
                webbrowser.open(f"http://localhost:{port}/index.html")
            except Exception as e:
                print(f"[!] Could not launch default browser: {e}")

    w_thread = threading.Thread(target=_watch, daemon=True)
    w_thread.start()


def main():
    config = load_config()
    eel.init('www')

    # Play startup chime asynchronously
    playAssistantSound("startup")

    # Start auto-listen if user configured it
    if config.get("auto_listen", False):
        cmd.toggleAutoListen(True)

    asst_name = config.get('assistant_name', 'Dragon').upper()
    port = find_available_port(8000)

    print("====================================================")
    print(f"            {asst_name} AI CORE v2.0 ONLINE")
    print("====================================================")
    print(f"[*] Core Web UI URL : http://localhost:{port}")
    print(f"[*] Alternative URL : http://127.0.0.1:{port}")
    print("[*] Status          : Initializing UI window...")
    print("[*] Controls        : Press Ctrl+C in this terminal to shutdown.")
    print("----------------------------------------------------")

    # Start fallback watchdog to guarantee UI responsiveness
    start_watchdog(port, timeout=6)

    # Determine browser modes to try.
    # On Windows, Edge ('mode=edge') provides the most reliable native app-window
    # experience without browser chrome or tabs, matching modern desktop HUD aesthetics.
    pref = config.get("browser", "edge").lower()
    candidate_modes = []
    if pref == "edge":
        candidate_modes = ["edge", "chrome", "default"]
    elif pref == "chrome":
        candidate_modes = ["chrome", "edge", "default"]
    else:
        candidate_modes = [pref, "edge", "chrome", "default"]

    # Filter unique modes preserving order
    modes_to_try = []
    for m in candidate_modes:
        if m not in modes_to_try:
            modes_to_try.append(m)

    started = False
    for mode in modes_to_try:
        try:
            print(f"[*] Starting UI in '{mode}' mode...")
            eel.start(
                'index.html',
                mode=mode,
                host='localhost',
                port=port,
                size=(1260, 860),
                block=True
            )
            started = True
            break
        except EnvironmentError as env_err:
            print(f"[!] Browser '{mode}' not available on system: {env_err}")
        except Exception as err:
            print(f"[!] '{mode}' mode encountered an error: {err}")

    if not started:
        print("[!] Falling back to system default browser...")
        try:
            eel.start(
                'index.html',
                mode='default',
                host='localhost',
                port=port,
                size=(1260, 860),
                block=True
            )
        except Exception as e:
            print(f"[!] Fatal error starting Eel web server: {e}")


if __name__ == '__main__':
    main()