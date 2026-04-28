# Jarvis AI Features And Interactions

## Overview

Jarvis AI is a Windows desktop voice assistant with a web-based interface powered by Eel. It supports voice input, text chat, face authentication, AI replies, app launching, web search, YouTube playback, weather updates, memory recall, WhatsApp actions, mobile calls, and chat history.

## Main Interactions

- Voice command input through the microphone.
- Text command input from the web interface.
- Assistant replies shown in the interface.
- Optional speech output through Windows SAPI voice.
- Chat history loading from local/cloud storage.
- Face authentication before the main assistant UI opens.
- Hotword listening with Picovoice Porcupine using the keywords `jarvis` and `alexa`.

## AI Chat

- Uses Groq chat completions.
- Model configured in the code: `llama-3.3-70b-versatile`.
- General questions are sent to the AI chatbot.
- Code-related questions are cleaned so the answer is returned as a single code block when possible.
- Requires `GROQ_API_KEY` in `.env`.

## Commands

### Open Apps Or Websites

Example commands:

- `open chrome`
- `open youtube`
- `open calculator`

Jarvis checks saved commands in the SQLite database first, then falls back to opening the requested app or URL through Windows.

### YouTube Playback

Example command:

- `play perfect on youtube`

Jarvis extracts the search term and plays it on YouTube using `pywhatkit`.

### Google Search

Example commands:

- `search Python tutorial`
- `google weather in Delhi`

Jarvis opens a Google search result page in the browser.

### Weather

Example commands:

- `weather in Lucknow`
- `what is the weather in Delhi`

Jarvis fetches temperature, weather description, and feels-like temperature from OpenWeather.

Requires `OPENWEATHER_API_KEY` in `.env`.

### Memory

Example commands:

- `remember my college is XYZ`
- `what is my college`

Jarvis stores and recalls simple question-answer memories using `jarvis.db`.

### WhatsApp Message, Call, And Video Call

Example commands:

- `send message to Rahul`
- `phone call Rahul`
- `video call Rahul`

Jarvis searches contacts in the database, asks for WhatsApp or mobile preference, and then opens WhatsApp or ADB call actions.

### Mobile Call With ADB

Jarvis can start a phone call through Android Debug Bridge using:

```text
adb shell am start -a android.intent.action.CALL -d tel:<number>
```

ADB and device setup are required for this feature.

## Authentication

- Face authentication is handled through OpenCV.
- The assistant starts only after successful face authentication.
- Face sample/trainer scripts are available under `engine/auth/`.

## Pattern Lock

- Android-style 3x3 pattern lock is shown after face authentication.
- First-time users must set and confirm a pattern before entering Jarvis.
- Existing users must draw the saved pattern to unlock Jarvis.
- Pattern can be changed from the settings button after unlocking.
- Pattern can be removed from the settings button after unlocking.
- Change and remove actions require the current pattern first.
- Pattern data is stored locally in `pattern_lock.json` as a salted SHA-256 hash.
- `pattern_lock.json` is ignored by Git and should not be uploaded.

## Interface

- Frontend files are in `www/`.
- Demo screenshots are stored in `www/assets/img/`.
- Audio startup sound is stored in `www/assets/audio/start_sound.mp3`.

## Environment Variables

Create a local `.env` file from `.env.example` and fill:

```env
GROQ_API_KEY=your_groq_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here
PICOVOICE_ACCESS_KEY=your_picovoice_access_key_here
```

Do not commit `.env` to GitHub.

## Local Data Files

- `jarvis.db`: local SQLite database for contacts, commands, and memory.
- `.contact.csv`: local contact import file.
- `firebase_key.json`: local Firebase credential file if cloud history is used.

These files should stay local and are ignored by Git.
