"""
JARVIFY — Spotify Voice Assistant
Vosk: local wake-word detection.
Faster-Whisper: local command transcription.
Spotify: desktop app control; no Spotify API or API keys.
"""

import os
import re
import json
import time
import threading
import ctypes
from pathlib import Path
from urllib.parse import quote

import numpy as np
import sounddevice as sd
import keyboard
import pyautogui
import pygetwindow as gw
from vosk import Model, KaldiRecognizer
from faster_whisper import WhisperModel
from colorama import Fore, Style, init


# -------------------- Configuration --------------------

BANNER_TEXT = "JOHN KRAMER IS BACK"
PROJECT_CREDIT = "github.com/johnkramerisback"

WAKE_WORD = "jarvis"
SAMPLE_RATE = 16000
BLOCK_SIZE = 4000
TRANSCRIPTION_MODEL = "small"  # Change to "medium" for higher accuracy.

BASE_DIR = Path(__file__).resolve().parent
VOSK_MODEL_PATH = BASE_DIR / "models" / "vosk-model-small-en-us-0.15"

WHISPER_MODEL = None
WAKE_ACTIVATION = threading.Event()
COMMAND_LOCK = threading.Lock()
STOP_EVENT = threading.Event()

init(autoreset=True)
pyautogui.PAUSE = 0.2


# -------------------- Terminal UI --------------------

def banner():
    os.system("cls" if os.name == "nt" else "clear")
    print(Fore.GREEN + Style.BRIGHT + r"""
     ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗██╗   ██╗
     ██║██╔══██╗██╔══██╗██║   ██║██║╚════╝  ╚██╗ ██╔╝
     ██║███████║██████╔╝██║   ██║██║█████╗   ╚████╔╝
██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║██╔══╝    ╚██╔╝
╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████╗   ██║
 ╚════╝ ╚═╝  ╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝   ╚═╝
    """)
    print(Fore.GREEN + Style.BRIGHT + f"       {BANNER_TEXT}")
    print(Fore.CYAN + f"       {PROJECT_CREDIT}")
    print(Fore.MAGENTA + "       LOCAL VOICE ASSISTANT\n")


def info(message):
    print(Fore.CYAN + "[JARVIFY] " + Style.RESET_ALL + message)


def success(message):
    print(Fore.GREEN + "[OK] " + Style.RESET_ALL + message)


def warning(message):
    print(Fore.YELLOW + "[NOTICE] " + Style.RESET_ALL + message)


def error(message):
    print(Fore.RED + "[ERROR] " + Style.RESET_ALL + message)


# -------------------- Model loading --------------------

def load_models():
    global WHISPER_MODEL

    if not VOSK_MODEL_PATH.is_dir():
        raise FileNotFoundError(
            f"Vosk model folder not found: {VOSK_MODEL_PATH}\n"
            "See README.md for setup instructions."
        )

    info("Loading Vosk wake-word model...")
    vosk_model = Model(str(VOSK_MODEL_PATH))
    success("Vosk ready.")

    info(f"Loading local transcription model: {TRANSCRIPTION_MODEL}")
    info("The first launch downloads the model and may take a while.")

    WHISPER_MODEL = WhisperModel(
        TRANSCRIPTION_MODEL,
        device="cpu",
        compute_type="int8",
    )
    success("Command transcription ready.")
    return vosk_model


# -------------------- Record and transcribe commands --------------------

def record_command(max_seconds=12, silence_seconds=1.3):
    """Record a phrase until speech is followed by silence."""
    info("Speak your command...")

    frames = []
    started_speech = False
    silence_duration = 0.0
    elapsed = 0.0
    energy_threshold = 0.012

    try:
        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="float32",
            blocksize=1024,
        ) as stream:
            while elapsed < max_seconds and not STOP_EVENT.is_set():
                audio, overflowed = stream.read(1024)
                chunk = audio[:, 0].copy()

                if overflowed:
                    continue

                duration = len(chunk) / SAMPLE_RATE
                elapsed += duration
                rms = float(np.sqrt(np.mean(chunk * chunk) + 1e-12))

                if rms >= energy_threshold:
                    started_speech = True
                    silence_duration = 0.0
                    frames.append(chunk)
                elif started_speech:
                    frames.append(chunk)
                    silence_duration += duration
                    if silence_duration >= silence_seconds:
                        break

        if not frames or not started_speech:
            warning("No clear speech detected. Try again.")
            return None

        return np.concatenate(frames).astype(np.float32)

    except Exception as exc:
        error(f"Recording failed: {exc}")
        return None


def transcribe_command(audio):
    """Transcribe speech locally; language is detected automatically."""
    if audio is None or len(audio) == 0:
        return ""

    try:
        segments, _ = WHISPER_MODEL.transcribe(
            audio,
            beam_size=5,
            vad_filter=True,
            condition_on_previous_text=False,
            initial_prompt=(
                "Voice assistant commands and Spotify music requests. "
                "Song titles and artist names may be in English or Hindi. "
                "Commands include play, pause, next song, previous song, "
                "volume up, volume down, and search."
            ),
        )
        text = " ".join(segment.text.strip() for segment in segments).strip()

        if text:
            print(Fore.WHITE + "You: " + text)
        else:
            warning("I couldn't understand the command.")

        return text

    except Exception as exc:
        error(f"Transcription failed: {exc}")
        return ""


# -------------------- Spotify desktop controls --------------------

def focus_spotify():
    try:
        windows = gw.getWindowsWithTitle("Spotify")
        for window in windows:
            if window.isMinimized:
                window.restore()
            window.activate()
            time.sleep(0.6)
            return True
    except Exception:
        pass
    return False


def spotify_search_and_play(query):
    """
    Open Spotify desktop search and press Enter to attempt to activate
    the currently selected result. No Spotify API is used.
    """
    query = query.strip()
    if not query:
        warning("Please say the song name.")
        return

    try:
        info(f"Searching Spotify for: {query}")
        spotify_uri = "spotify:search:" + quote(query, safe="")
        os.startfile(spotify_uri)
        time.sleep(3)

        if not focus_spotify():
            warning("Could not focus Spotify. Open Spotify and retry.")
            return

        pyautogui.press("enter")
        time.sleep(0.5)
        success(f"Playback command sent: {query}")

    except Exception as exc:
        error(f"Spotify control failed: {exc}")


# -------------------- Windows media keys --------------------

def media_key(key_code):
    try:
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        key_up = 0x0002
        user32.keybd_event(key_code, 0, 0, 0)
        user32.keybd_event(key_code, 0, key_up, 0)
    except Exception as exc:
        error(f"Media key failed: {exc}")


def play_pause():
    media_key(0xB3)
    success("Play / pause")


def next_track():
    media_key(0xB0)
    success("Next track")


def previous_track():
    media_key(0xB1)
    success("Previous track")


def volume_up():
    media_key(0xAF)
    success("Volume up")


def volume_down():
    media_key(0xAE)
    success("Volume down")


def mute_volume():
    media_key(0xAD)
    success("Mute toggled")


# -------------------- Command parsing --------------------

def normalize_command(text):
    text = text.lower().strip()
    text = re.sub(r"[^\w\s'-]", " ", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"^(?:hey\s+)?jarvis\b\s*", "", text)
    return text.strip()


def extract_play_query(command):
    patterns = [
        r"^(?:please\s+)?play\s+(?:me\s+)?(?:the\s+)?song\s+(.+)$",
        r"^(?:please\s+)?play\s+(.+)$",
        r"^search\s+(?:for\s+)?(.+?)(?:\s+on\s+spotify)?$",
        r"^find\s+(?:the\s+)?song\s+(.+)$",
        r"^(?:gaana|song)\s+chalao\s+(.+)$",
        r"^chalao\s+(.+)$",
        r"^bajao\s+(.+)$",
        r"^(.+?)\s+(?:gaana|song)\s+(?:chalao|bajao)$",
        r"^(.+?)\s+spotify\s+par\s+chalao$",
    ]

    for pattern in patterns:
        match = re.match(pattern, command)
        if match:
            query = match.group(1).strip()
            query = re.sub(r"\s+on spotify$", "", query)
            return query

    return None


def handle_command(raw_text):
    command = normalize_command(raw_text)
    if not command:
        warning("No command detected.")
        return

    info(f"Command: {command}")

    controls = {
        "pause": play_pause,
        "pause music": play_pause,
        "pause the music": play_pause,
        "stop music": play_pause,
        "pause kar": play_pause,
        "gaana rok": play_pause,
        "music rok": play_pause,
        "rok do": play_pause,
        "resume": play_pause,
        "resume music": play_pause,
        "continue music": play_pause,
        "unpause": play_pause,
        "unpause music": play_pause,
        "next": next_track,
        "next song": next_track,
        "next track": next_track,
        "skip": next_track,
        "skip song": next_track,
        "agla gaana": next_track,
        "agla song": next_track,
        "previous": previous_track,
        "previous song": previous_track,
        "previous track": previous_track,
        "last song": previous_track,
        "pichla gaana": previous_track,
        "pichla song": previous_track,
        "volume up": volume_up,
        "increase volume": volume_up,
        "volume badhao": volume_up,
        "awaaz badhao": volume_up,
        "volume down": volume_down,
        "decrease volume": volume_down,
        "volume kam": volume_down,
        "awaaz kam": volume_down,
        "mute": mute_volume,
        "mute volume": mute_volume,
        "awaaz band": mute_volume,
    }

    if command in controls:
        controls[command]()
        return

    if command in {"open spotify", "spotify kholo"}:
        try:
            os.startfile("spotify:")
            success("Opening Spotify.")
        except Exception as exc:
            error(f"Could not open Spotify: {exc}")
        return

    if command in {"exit", "quit", "shutdown jarvis", "band ho jao"}:
        STOP_EVENT.set()
        return

    query = extract_play_query(command)
    if query:
        spotify_search_and_play(query)
        return

    warning(f"Command not recognized: {raw_text}")
    info("Examples: 'play Set Fire to the Rain', 'pause', 'next song'.")


# -------------------- Wake word and activation --------------------

def activate_command():
    WAKE_ACTIVATION.set()


def process_command():
    if not COMMAND_LOCK.acquire(blocking=False):
        warning("A command is already being processed.")
        return

    try:
        audio = record_command()
        text = transcribe_command(audio)
        if text:
            handle_command(text)
    finally:
        COMMAND_LOCK.release()


def wake_word_loop(vosk_model):
    recognizer = KaldiRecognizer(vosk_model, SAMPLE_RATE)
    info("Say 'Jarvis' to activate.")
    info("Or press Ctrl + Space to speak.")
    info("Listening for wake word...")

    while not STOP_EVENT.is_set():
        try:
            if WAKE_ACTIVATION.is_set():
                WAKE_ACTIVATION.clear()
                process_command()
                recognizer = KaldiRecognizer(vosk_model, SAMPLE_RATE)
                continue

            activated = False
            with sd.RawInputStream(
                samplerate=SAMPLE_RATE,
                blocksize=BLOCK_SIZE,
                dtype="int16",
                channels=1,
            ) as stream:
                while not STOP_EVENT.is_set():
                    if WAKE_ACTIVATION.is_set():
                        WAKE_ACTIVATION.clear()
                        activated = True
                        break

                    data, overflowed = stream.read(BLOCK_SIZE)
                    if overflowed:
                        continue

                    if recognizer.AcceptWaveform(bytes(data)):
                        result = json.loads(recognizer.Result())
                        words = result.get("text", "").lower().split()
                        if WAKE_WORD in words:
                            activated = True
                            success("Jarvis activated.")
                            break

            if activated and not STOP_EVENT.is_set():
                process_command()
                recognizer = KaldiRecognizer(vosk_model, SAMPLE_RATE)

        except KeyboardInterrupt:
            STOP_EVENT.set()
            break
        except Exception as exc:
            error(f"Audio error: {exc}")
            time.sleep(1)


# -------------------- Hotkeys and main --------------------

def register_hotkeys():
    keyboard.add_hotkey("ctrl+space", activate_command)
    keyboard.add_hotkey("ctrl+alt+p", play_pause)
    keyboard.add_hotkey("ctrl+alt+n", next_track)
    keyboard.add_hotkey("ctrl+alt+b", previous_track)

    info("Ctrl + Space     Speak a command")
    info("Ctrl + Alt + P   Play / pause")
    info("Ctrl + Alt + N   Next track")
    info("Ctrl + Alt + B   Previous track")


def main():
    if os.name != "nt":
        error("This version is designed for Windows.")
        raise SystemExit(1)

    banner()
    try:
        vosk_model = load_models()
        register_hotkeys()
        wake_word_loop(vosk_model)
    except KeyboardInterrupt:
        info("JARVIFY stopped.")
    except Exception as exc:
        error(f"Startup failed: {exc}")
        raise SystemExit(1)
    finally:
        STOP_EVENT.set()
        keyboard.unhook_all()


if __name__ == "__main__":
    main()
