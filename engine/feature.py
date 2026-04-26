import os
import re
from shlex import quote
import sqlite3
import struct
import subprocess
import time
import webbrowser
from groq import Groq

from playsound import playsound
import eel
import pvporcupine
import pyaudio
import pyautogui
from engine.command import speak
from engine.config import ASSISTEANT_NAME
import pywhatkit as kit
from engine.helper import extract_yt_term, remove_words

con = sqlite3.connect("jarvis.db")
cursor = con.cursor()


def load_local_env():
    env_path = ".env"
    if not os.path.exists(env_path):
        return

    with open(env_path, "r", encoding="utf-8") as env_file:
        for line in env_file:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_local_env()


def extract_city_from_weather_query(query):
    query = (query or "").lower().strip()
    query = re.sub(rf"\b{re.escape(ASSISTEANT_NAME.lower())}\b", "", query)

    patterns = [
        r"weather\s+(?:in|of|at|for)\s+([a-zA-Z\s]+)",
        r"(?:what(?:'s| is)?\s+the\s+)?weather\s+([a-zA-Z\s]+)",
        r"([a-zA-Z\s]+)\s+weather",
    ]

    for pattern in patterns:
        match = re.search(pattern, query)
        if match:
            city = re.sub(r"\b(today|now|right now|please)\b", "", match.group(1), flags=re.IGNORECASE)
            city = re.sub(r"\s+", " ", city).strip(" ?.,")
            if city:
                return city.title()

    cleaned_query = re.sub(r"\b(weather|ka|ki|kya|hai|bataye|batao|please|jarvis)\b", "", query)
    cleaned_query = re.sub(r"\s+", " ", cleaned_query).strip(" ?.,")
    if cleaned_query:
        return cleaned_query.title()

    return None


@eel.expose
def playAssistantSound():
    music_dir = "www\\assets\\audio\\start_sound.mp3"
    playsound(music_dir)

def openCommand(query):
    query = query.replace(ASSISTEANT_NAME, "")
    query = query.replace("open", "")
    query.lower()

    app_name = query.strip()

    if app_name!="":
        try:
            cursor.execute(
                'SELECT path FROM sys_command WHERE name IN (?)', (app_name,))
            results = cursor.fetchall()

            if len(results) != 0:
                speak("Opening "+query)
                os.startfile(results[0][0])

            elif len(results) == 0: 
                cursor.execute(
                'SELECT url FROM web_command WHERE name IN (?)', (app_name,))
                results = cursor.fetchall()
                
                if len(results) != 0:
                    speak("Opening "+query)
                    webbrowser.open(results[0][0])

                else:
                    speak("Opening "+query)
                    try:
                        os.system('start '+query)
                    except:
                        speak("not found")
        except:
            speak("some thing went wrong")

def PlayYoutube(query):
    search_term = extract_yt_term(query)
    speak("Playing "+search_term+" on YouTube")
    kit.playonyt(search_term)

def hotword():
    porcupine = None
    paud = None
    audio_stream = None

    try:
        access_key = os.getenv("PICOVOICE_ACCESS_KEY")
        if not access_key:
            print("Picovoice access key is missing")
            return

        porcupine = pvporcupine.create(
            access_key=access_key,
            keywords=["jarvis", "alexa"],
            sensitivities=[0.8, 0.8]
        )

        paud = pyaudio.PyAudio()

        audio_stream = paud.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length
        )

        print("Listening for hotword...")

        while True:
            pcm = audio_stream.read(porcupine.frame_length)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

            keyword_index = porcupine.process(pcm)

            if keyword_index >= 0:
                print("Hotword Detected!")

    except Exception as e:
        print("Error:", e)

    finally:
        if porcupine:
            porcupine.delete()
        if audio_stream:
            audio_stream.close()
        if paud:
            paud.terminate()

def findContact(query):
    
    words_to_remove = [ASSISTEANT_NAME, 'make', 'a', 'to', 'phone', 'call', 'send', 'message', 'wahtsapp', 'video']
    query = remove_words(query, words_to_remove)

    try:
        query = query.strip().lower()
        cursor.execute("SELECT mobile_no FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", ('%' + query + '%', query + '%'))
        results = cursor.fetchall()
        print(results[0][0])
        mobile_number_str = str(results[0][0])

        if not mobile_number_str.startswith('+91'):
            mobile_number_str = '+91' + mobile_number_str

        return mobile_number_str, query
    except:
        speak('not exist in contacts')
        return 0, 0
    
def whatsApp(mobile_no, message, flag, name):
    

    if flag == 'message':
        target_tab = 12
        jarvis_message = "message send successfully to "+name

    elif flag == 'call':
        target_tab = 7
        message = ''
        jarvis_message = "calling to "+name

    else:
        target_tab = 6
        message = ''
        jarvis_message = "staring video call with "+name


    encoded_message = quote(message)
    print(encoded_message)
    whatsapp_url = f"whatsapp://send?phone={mobile_no}&text={encoded_message}"

    full_command = f'start "" "{whatsapp_url}"'
    subprocess.run(full_command, shell=True)
    time.sleep(5)
    subprocess.run(full_command, shell=True)
    
    pyautogui.hotkey('ctrl', 'f')

    for i in range(1, target_tab):
        pyautogui.hotkey('tab')

    pyautogui.hotkey('enter')
    speak(jarvis_message)

client = None

def chatBot(query):
    try:
        global client
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            speak("Groq API key is missing")
            return

        if client is None:
            client = Groq(api_key=api_key)

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
            {"role": "system", "content": "You are Jarvis AI. If the user asks for code, respond ONLY with clean code inside one proper triple-backtick code block. Do not add explanations, headings, markdown outside the code block, or extra text."},
            {"role": "user", "content": query}
            ]
        )

        reply = response.choices[0].message.content
        code_words = ["code", "program", "script", "function", "html", "css", "javascript", "python", "java", "c++"]

        if any(word in query.lower() for word in code_words):
            code_match = re.search(r"```[a-zA-Z0-9_+-]*\s*([\s\S]*?)```", reply)
            if code_match:
                reply = "```\n" + code_match.group(1).strip() + "\n```"

        print(reply)
        return reply

    except Exception as e:
        speak("Error connecting to AI")
        print(e)

def makeCall(name, mobileNo):
    mobileNo =mobileNo.replace(" ", "")
    speak("Calling "+name)
    command = 'adb shell am start -a android.intent.action.CALL -d tel:'+mobileNo
    os.system(command)

def searchGoogle(query):
    import webbrowser
    
    query = query.replace("search", "")
    query = query.replace("google", "")
    query = query.replace("on google", "")
    query = query.strip()

    speak("Searching " + query + " on Google")

    url = "https://www.google.com/search?q=" + query
    webbrowser.open(url)

memory = {}

import sqlite3
from engine.command import speak

def rememberSomething(query):

    query = query.replace("remember", "")
    query = query.replace("jarvis", "")
    query = query.strip()

    if " is " in query:
        question, answer = query.split(" is ",1)

        con = sqlite3.connect("jarvis.db")
        cursor = con.cursor()

        cursor.execute(
        "INSERT INTO memory(question,answer) VALUES (?,?)",
        (question.strip(), answer.strip())
        )

        con.commit()
        con.close()

        speak("I will remember that " + question + " is " + answer)


def recallMemory(query):

    from engine.command import speak
    import sqlite3

    query = query.replace("jarvis","")
    query = query.replace("what is","")
    query = query.strip()

    con = sqlite3.connect("jarvis.db")
    cursor = con.cursor()

    cursor.execute(
    "SELECT answer FROM memory WHERE question=?",
    (query,)
    )

    result = cursor.fetchone()
    con.close()

    if result:
        speak(query + " is " + result[0])
    else:
        speak("I don't remember that yet")

def getWeather(city):
    import requests

    api_key = os.getenv("OPENWEATHER_API_KEY")

    if not api_key:
        speak("OpenWeather API key is missing")
        return

    if not city:
        speak("Please tell me the city name for the weather update")
        return

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric",
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if response.status_code != 200 or "main" not in data or "weather" not in data:
            speak(f"I could not find weather details for {city}")
            return

        temp = data["main"]["temp"]
        feels_like = data["main"].get("feels_like")
        desc = data["weather"][0]["description"]

        if feels_like is not None:
            speak(f"Temperature in {city} is {temp} degree Celsius with {desc}. It feels like {feels_like} degree Celsius.")
        else:
            speak(f"Temperature in {city} is {temp} degree Celsius with {desc}")

    except Exception:
        speak("Unable to fetch weather right now")
