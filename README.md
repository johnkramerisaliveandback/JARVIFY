# JARVIFY — Spotify Voice Assistant

JARVIFY is a Windows voice assistant that lets you control Spotify Desktop with voice commands. It uses Vosk for local wake-word detection and Faster-Whisper for local speech transcription, then controls Spotify through its desktop URI handler and Windows media keys.

**No Spotify API credentials or API keys are required.** JARVIFY does not use Spotify's Web API.

## Features

- Local wake-word detection using Vosk (`Jarvis`)
- Local speech-to-text using Faster-Whisper
- Automatic language detection for command transcription
- Song searches through Spotify Desktop
- Play/pause, next track, previous track, volume, and mute controls
- English and common Hinglish commands
- Keyboard shortcuts:
  - `Ctrl + Space`: listen for a command
  - `Ctrl + Alt + P`: play/pause
  - `Ctrl + Alt + N`: next track
  - `Ctrl + Alt + B`: previous track

## Requirements

- Windows 10 or Windows 11
- Python 3.11 or 3.12 recommended
- Spotify Desktop installed and signed in
- A working microphone
- An internet connection for Spotify and for first-time package/model downloads

## Installation

### 1. Download the project

**Option A — Clone with Git**

Install Git for Windows if you don't already have it, then run these commands in PowerShell:

```powershell
git clone https://github.com/johnkramerisaliveandback/JARVIFY.git
cd JARVIFY
```

**Option B — Download a ZIP**

Open the [JARVIFY repository](https://github.com/johnkramerisaliveandback/JARVIFY), click **Code → Download ZIP**, then extract the ZIP. Open PowerShell in the extracted `JARVIFY` folder.

### 2. Create a virtual environment

The commands below use Python 3.12. If you installed Python 3.11 instead, replace `3.12` with `3.11`.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

If PowerShell blocks environment activation, you can use the environment's Python directly:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
```

### 3. Install Python libraries

With the virtual environment activated, run:

```powershell
python -m pip install -r requirements.txt
```

### 4. Download the Vosk wake-word model

Download the official **vosk-model-small-en-us-0.15** model from the [Vosk models page](https://alphacephei.com/vosk/models). You can also use the [direct ZIP download](https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip).

Extract it into a folder named `models` inside the project directory. The final path must be:

```text
JARVIFY/
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

The `am` and `conf` directories should be directly inside `vosk-model-small-en-us-0.15`. Avoid leaving the model nested inside a second folder with the same name.

The Vosk model is not included in the repository because it is a separate download. The project uses this model to listen for the English wake word, “Jarvis.”

### 5. Run JARVIFY

Make sure Spotify Desktop is installed and signed in, then run:

```powershell
python spotify_voice.py
```

On the first launch, Faster-Whisper downloads its configured transcription model. This download may take some time. Later launches can use the downloaded model locally.

## Usage examples

Say **“Jarvis”**, wait for the activation message, and then speak your command.

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

The default Faster-Whisper model is `small`. It offers a balance between recognition quality and resource use, but speed depends on your CPU, memory, and other system hardware.

To try a larger model, open `spotify_voice.py` and change:

```python
TRANSCRIPTION_MODEL = "small"
```

to:

```python
TRANSCRIPTION_MODEL = "medium"
```

The `medium` model needs more storage and RAM and may run considerably slower on a CPU.

Vosk detects the wake word, and Faster-Whisper transcribes the command after activation. Both perform inference locally once their model files have been downloaded.

## Spotify playback behavior

JARVIFY does not use the Spotify Web API. It opens a Spotify Desktop search URI and sends an Enter key to try to activate the selected result. Spotify's current interface, window focus, and result selection can affect whether the intended track starts. If the result is not selected automatically, bring Spotify to the foreground and select it manually.

Windows media keys control whichever application currently responds to those keys, so they may affect another media app if it has focus or is handling media controls.

## Privacy

- Wake-word detection runs locally with Vosk.
- Voice-command transcription runs locally with Faster-Whisper after its model has been downloaded.
- The project does not require Spotify API keys, access tokens, or client secrets.
- Song searches are sent to Spotify Desktop when you ask JARVIFY to search for or play a song.
- Internet access is needed for Spotify, package installation, and initial model downloads.

## Troubleshooting

### Microphone is not detected

- Open **Windows Settings → Privacy & security → Microphone**.
- Allow desktop apps to access the microphone.
- Check the default recording device in Windows Sound settings.
- Close other applications that may be using the microphone.

### `No module named ...`

Make sure the virtual environment is activated, then run:

```powershell
python -m pip install -r requirements.txt
```

### Vosk model not found

Check that this folder exists relative to `spotify_voice.py`:

```text
models\vosk-model-small-en-us-0.15
```

The model folder should contain directories such as `am` and `conf`.

### Spotify search opens but the song does not start

Bring Spotify Desktop to the foreground and select the result manually. The desktop URI and keyboard approach depends on Spotify's current interface and focus; it cannot guarantee automatic selection of the top result.

### Speech recognition is inaccurate

Speak clearly after the wake-word confirmation and reduce background noise. You can try the `medium` transcription model if your computer has enough memory.

## License

JARVIFY is provided under the **JARVIFY Personal-Use License** in the [LICENSE](LICENSE) file.

You may download and use it for personal purposes. You may **not** re-upload, redistribute, republish, sell, or publish modified versions, or claim the project/source code as your own, unless you have prior written permission from the copyright holder. All other rights are reserved.

This is a restrictive, custom license—not an open-source license such as MIT. Public visibility on GitHub does not mean the code is free to relicense or redistribute. See [LICENSE](LICENSE) for the complete terms.
