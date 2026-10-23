# JARVIFY — Spotify Voice Assistant

A Windows voice assistant that uses Vosk for local wake-word detection and Faster-Whisper for local speech transcription. It controls Spotify Desktop through Spotify's URI handler and Windows media keys.

**No Spotify API credentials or API keys are required.** The project does not use Spotify's Web API.

## Features

- Local wake-word detection using Vosk (`Jarvis`)
- Local speech-to-text using Faster-Whisper
- Automatically detects the spoken language for command transcription
- Play/search song requests through Spotify Desktop
- Play/pause, next track, previous track, volume, and mute controls
- English and common Hinglish commands
- Keyboard shortcuts:
  - `Ctrl + Space`: listen for a command
  - `Ctrl + Alt + P`: play/pause
  - `Ctrl + Alt + N`: next track
  - `Ctrl + Alt + B`: previous track

## Requirements

- Windows 10 or Windows 11
- Python 3.10–3.13 (Python 3.11 or 3.12 is often the easiest option for ML/audio packages)
- Spotify Desktop installed
- A working microphone
- Internet access for the initial model downloads only

## Installation

### 1. Download the project

Download the ZIP from the GitHub repository where you upload these files, or clone that repository using its actual URL:

```powershell
git clone <YOUR_REPOSITORY_URL>
cd <YOUR_REPOSITORY_FOLDER>
```

Replace the placeholders with your repository URL and folder name.

### 2. Create a virtual environment

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

If PowerShell blocks activation, you can install packages without activating the environment by using `py -3.13 -m pip ...`.

### 3. Install Python libraries

```powershell
python -m pip install -r requirements.txt
```

### 4. Install the Vosk wake-word model

Download the **vosk-model-small-en-us-0.15** model from the official Vosk model page:

https://alphacephei.com/vosk/models

Extract the downloaded archive so the folder structure is:

```text
jarvify/
├── spotify_voice.py
├── requirements.txt
├── README.md
└── models/
    └── vosk-model-small-en-us-0.15/
        ├── am/
        ├── conf/
        ├── graph/
        └── ...
```

Do not leave the model nested inside another folder with the same name. The `am` directory should be directly inside `vosk-model-small-en-us-0.15`.

The model is not included in this GitHub source ZIP because it is a separate, comparatively large download.

### 5. Run JARVIFY

Make sure Spotify Desktop is installed and signed in, then run:

```powershell
python spotify_voice.py
```

The first launch of Faster-Whisper downloads the selected transcription model. Later launches can use the downloaded model locally.

## Usage examples

Say **“Jarvis”**, wait for the activation message, then speak your command.

Examples:

- “Play Set Fire to the Rain”
- “Play Believer by Imagine Dragons”
- “Search for Diet Pepsi”
- “Pause”
- “Resume”
- “Next song”
- “Previous song”
- “Volume up”
- “Volume down”
- “Mute”
- “Open Spotify”

You can also press `Ctrl + Space` to start a command without saying the wake word.

## Speech recognition model

The default Faster-Whisper model is `small`, which balances recognition quality and CPU use. The model downloads automatically the first time it runs.

To try a larger model, open `spotify_voice.py` and change:

```python
TRANSCRIPTION_MODEL = "small"
```

to:

```python
TRANSCRIPTION_MODEL = "medium"
```

The `medium` model needs more RAM and runs more slowly on CPU.

Vosk is used for detecting the wake word. Faster-Whisper transcribes the command after activation. Both models run locally after their files have been downloaded.

## Spotify playback behavior

This project does not use the Spotify API. It opens a Spotify Desktop search URI and sends an Enter key to attempt to activate the selected result. Spotify's interface, window focus, and result selection can affect whether the correct track starts. If the result is not selected, choose it manually in Spotify.

The media-key shortcuts control whichever application currently responds to Windows media keys.

## Privacy

- Wake-word detection runs locally with Vosk.
- Voice-command transcription runs locally with Faster-Whisper after the model has downloaded.
- The script contains no API keys, access tokens, client secrets, or Spotify API integration.
- A song query is sent to the Spotify Desktop application when you ask to search/play a song.
- Initial Python package and model downloads require internet access.

## Troubleshooting

### Microphone is not detected

- Open **Windows Settings → Privacy & security → Microphone**.
- Allow desktop apps to access the microphone.
- Check the default recording device in Windows Sound settings.
- Close other applications that may be exclusively using the microphone.

### `No module named ...`

Activate the virtual environment and run:

```powershell
python -m pip install -r requirements.txt
```

### Vosk model not found

Check that this folder exists:

```text
models\vosk-model-small-en-us-0.15
```

The folder must contain subfolders such as `am` and `conf`.

### Spotify search opens but the song does not start

Bring Spotify Desktop to the foreground and select the result manually. The desktop URI and keyboard approach depends on Spotify's current interface and focus; it does not guarantee automatic selection of the top result.

### Speech recognition is inaccurate

Speak clearly after the wake-word confirmation. Try a larger model such as `medium` if your computer has enough memory.

## License

No license file is included. Add a license if you want to specify how others may reuse or distribute this project.
