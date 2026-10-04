import os
import re
from shlex import quote
import sqlite3
import subprocess
import time
import webbrowser
from datetime import datetime
from groq import Groq

from playsound import playsound
import eel
import pyautogui
from engine.command import speak
from engine.config import ASSISTEANT_NAME
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
    import pywhatkit as kit

    search_term = extract_yt_term(query)
    speak("Playing "+search_term+" on YouTube")
    kit.playonyt(search_term)

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

# Groq retires and adds models over time. These are only preferences; the
# runtime checks the account's own model list before selecting one.
GROQ_MODEL_PREFERENCES = [
    "qwen/qwen3-32b",
    "llama-3.1-8b-instant",
    "meta-llama/llama-4-scout-17b-16e-instruct",
    # Some gpt-oss responses attempt tool calls even when Jarvis provides no
    # tools, so keep it as the final fallback.
    "openai/gpt-oss-20b",
]


def get_groq_model(excluded_models=None):
    """Return an accessible Groq chat model, respecting GROQ_MODEL if set."""
    excluded_models = set(excluded_models or [])
    configured_model = os.getenv("GROQ_MODEL", "").strip()
    if configured_model and configured_model not in excluded_models:
        return configured_model

    try:
        available_models = [item.id for item in client.models.list().data]
        for model in GROQ_MODEL_PREFERENCES:
            if model in available_models and model not in excluded_models:
                return model

        # Prefer an instruction/chat model if the account offers a newer name.
        for model in available_models:
            lower_name = model.lower()
            if model not in excluded_models and ("instruct" in lower_name or "chat" in lower_name):
                return model

        for model in available_models:
            if model not in excluded_models:
                return model
    except Exception as exc:
        print(f"Could not fetch Groq model list: {exc}")

    # Kept only as an offline fallback; normally an account-specific model
    # selected above is used.
    return "llama-3.1-8b-instant"


def is_tool_use_error(exc):
    error_text = str(exc).lower()
    return "tool_use_failed" in error_text or "model called a tool" in error_text

CODE_REQUEST_WORDS = [
    "code",
    "program",
    "script",
    "function",
    "html",
    "css",
    "javascript",
    "python",
    "java",
    "c++",
]

CURRENT_INFO_WORDS = [
    "current",
    "latest",
    "today",
    "todays",
    "today's",
    "news",
    "breaking",
    "live",
    "right now",
    "abhi",
    "aaj",
    "taaza",
    "taza",
    "naya",
    "new update",
    "price",
    "score",
    "weather",
    "date",
    "time",
    "chief minister",
    "cm",
    "prime minister",
    "president",
    "governor",
    "mayor",
    "ceo",
    "incumbent",
]

OFFICE_LOOKUP_WORDS = [
    "chief minister",
    "cm",
    "prime minister",
    "president",
    "governor",
    "mayor",
    "ceo",
    "incumbent",
]


def is_code_request(query):
    query = (query or "").lower()
    return any(word in query for word in CODE_REQUEST_WORDS)


def is_current_info_request(query):
    query = (query or "").lower()
    return any(word in query for word in CURRENT_INFO_WORDS)


def is_office_lookup_request(query):
    query = (query or "").lower()
    return any(word in query for word in OFFICE_LOOKUP_WORDS)


def get_local_current_answer(query):
    query = (query or "").lower()
    now = datetime.now()

    asks_date = (
        "date" in query
        or "tarikh" in query
        or "tareekh" in query
        or "aaj ki date" in query
        or "today's date" in query
    )
    asks_time = "time" in query or "samay" in query

    if asks_date and asks_time:
        return now.strftime("Current date is %d %B %Y and time is %I:%M %p.")
    if asks_date and not any(word in query for word in ["news", "latest", "current affairs", "price", "score"]) and not is_office_lookup_request(query):
        return now.strftime("Today's date is %d %B %Y.")
    if asks_time:
        return now.strftime("Current time is %I:%M %p.")

    return ""


def clean_search_text(value):
    value = re.sub(r"\s+", " ", value or "").strip()
    return value


def normalize_office_search_query(query):
    normalized = (query or "").lower()
    normalized = re.sub(r"\b(who|what|which)\s+(is|are|was|were)\b", " ", normalized)
    normalized = re.sub(r"\b(current|latest|today|right now|now|present|incumbent)\b", " ", normalized)
    normalized = re.sub(r"\b(the|a|an)\b", " ", normalized)
    normalized = re.sub(r"\bcm\b", "chief minister", normalized)
    normalized = normalized.replace("?", " ")
    return clean_search_text(normalized)


def build_search_queries(query):
    query = clean_search_text(query)
    if not query:
        return []

    if is_office_lookup_request(query):
        office_query = normalize_office_search_query(query)
        queries = [office_query or query]
        queries.extend([
            f"{office_query or query} incumbent official",
            f"{office_query or query} wikipedia",
            query,
        ])
    else:
        queries = [query]

    unique_queries = []
    for item in queries:
        if item not in unique_queries:
            unique_queries.append(item)

    return unique_queries


def search_web_current(query, limit=5):
    import requests
    from bs4 import BeautifulSoup
    from urllib.parse import quote_plus
    import xml.etree.ElementTree as ET

    search_queries = build_search_queries(query)
    if not search_queries:
        return []

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    results = []

    primary_query = search_queries[0]
    should_search_news = (
        not is_office_lookup_request(primary_query)
        and ("news" in primary_query.lower() or "latest" in primary_query.lower() or "today" in primary_query.lower())
    )

    if should_search_news:
        news_url = f"https://news.google.com/rss/search?q={quote_plus(primary_query)}&hl=en-IN&gl=IN&ceid=IN:en"
        try:
            response = requests.get(news_url, headers=headers, timeout=12)
            response.raise_for_status()
            root = ET.fromstring(response.content)
            for item in root.findall(".//item"):
                title = clean_search_text(item.findtext("title", ""))
                snippet = clean_search_text(item.findtext("description", ""))
                link = clean_search_text(item.findtext("link", ""))

                if title:
                    results.append({
                        "title": title,
                        "snippet": re.sub(r"<[^>]+>", "", snippet),
                        "link": link,
                    })

                if len(results) >= limit:
                    return results
        except Exception as exc:
            print("Google News search failed:", exc)

    search_urls = []
    for search_query in search_queries:
        search_urls.extend([
            f"https://duckduckgo.com/html/?q={quote_plus(search_query)}",
            f"https://www.bing.com/search?q={quote_plus(search_query)}",
        ])

    for url in search_urls:
        try:
            response = requests.get(url, headers=headers, timeout=12)
            response.raise_for_status()
        except Exception as exc:
            print("Search request failed:", exc)
            continue

        soup = BeautifulSoup(response.text, "html.parser")

        if "duckduckgo.com" in url:
            result_nodes = soup.select(".result")
            title_selector = ".result__a"
            snippet_selector = ".result__snippet"
        else:
            result_nodes = soup.select("li.b_algo")
            title_selector = "h2 a"
            snippet_selector = ".b_caption p"

        for result in result_nodes:
            title_node = result.select_one(title_selector)
            snippet_node = result.select_one(snippet_selector)

            if not title_node:
                continue

            title = clean_search_text(title_node.get_text(" ", strip=True))
            snippet = clean_search_text(snippet_node.get_text(" ", strip=True) if snippet_node else "")
            link = title_node.get("href", "")

            if title and (snippet or link):
                results.append({
                    "title": title,
                    "snippet": snippet,
                    "link": link,
                })

            if len(results) >= limit:
                return results

    return results


def extract_direct_current_answer(query, web_context):
    if not web_context or not is_office_lookup_request(query):
        return ""

    compact_context = clean_search_text(web_context)
    patterns = [
        r"\bheaded\s+by\s+([A-Z][A-Za-z .'-]{2,80})\s+who\s+was\s+sworn\s+in\s+as\s+the\s+Chief\s+Minister",
        r"\b([A-Z][A-Za-z .'-]{2,80})\s+who\s+was\s+sworn\s+in\s+as\s+the\s+Chief\s+Minister",
        r"\b([A-Z][A-Za-z .'-]{2,80})\s+was\s+sworn\s+in\s+as\s+[^.]{0,80}?Chief\s+Minister",
        r"\bcurrent\s+[^.]{0,80}?\s+is\s+([A-Z][A-Za-z .'-]{2,80})",
        r"\bincumbent\s*:\s*([A-Z][A-Za-z .'-]{2,80})",
        r"\bChief Minister\s+of\s+West\s+Bengal\s*\|\s*([A-Z][A-Za-z .'-]{2,80})",
        r"\b([A-Z][A-Za-z .'-]{2,80})\s+(?:was sworn in|assumed the office|is the current)",
    ]

    for pattern in patterns:
        match = re.search(pattern, compact_context)
        if match:
            name = clean_search_text(match.group(1))
            name = re.split(r"\s+(?:who|which|and|on|from|since|as)\b", name)[0].strip(" .,-")
            if name and len(name.split()) <= 5:
                return f"Based on live search results, the current answer is: {name}."

    return ""


def build_web_context(query):
    try:
        results = search_web_current(query)
    except Exception as exc:
        print("Live search failed:", exc)
        return ""

    if not results:
        return ""

    lines = []
    for index, item in enumerate(results, start=1):
        lines.append(
            f"{index}. {item['title']}\n"
            f"Snippet: {item['snippet']}\n"
            f"Source: {item['link']}"
        )

    return "\n\n".join(lines)


def detect_code_language(query, fallback=""):
    query = (query or "").lower()
    language_map = {
        "python": "python",
        "html": "html",
        "css": "css",
        "javascript": "javascript",
        "java": "java",
        "c++": "cpp",
    }

    for word, language in language_map.items():
        if word in query:
            return language

    return fallback


def format_code_reply(reply, query=""):
    reply = (reply or "").strip()
    code_match = re.search(r"```([a-zA-Z0-9_+-]*)\s*([\s\S]*?)```", reply)

    if code_match:
        language = detect_code_language(query, code_match.group(1).strip())
        code = code_match.group(2).strip()
    else:
        language = detect_code_language(query)
        lines = []
        for line in reply.splitlines():
            stripped = line.strip()
            if not stripped:
                if lines:
                    lines.append("")
                continue
            if stripped.lower().startswith(("output:", "result:", "explanation:", "here is", "sure,")):
                continue
            lines.append(line.rstrip())
        code = "\n".join(lines).strip()

    language_tag = language or ""
    return f"```{language_tag}\n{code}\n```" if code else ""


def chatBot(query):
    try:
        global client
        local_current_answer = get_local_current_answer(query)
        if local_current_answer:
            print(local_current_answer)
            return local_current_answer

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            speak("Groq API key is missing")
            return

        if client is None:
            client = Groq(api_key=api_key)

        today = datetime.now().strftime("%d %B %Y")
        web_context = ""
        if is_current_info_request(query) and not is_code_request(query):
            web_context = build_web_context(query)
            direct_answer = extract_direct_current_answer(query, web_context)
            if direct_answer:
                print(direct_answer)
                return direct_answer

        system_prompt = (
            "You are Jarvis AI. "
            f"Today's date is {today}. "
            "For current, latest, today, news, price, score, or live-data questions, use the provided live web context. "
            "If live web context is present, answer from it directly. If live web context is missing or truly insufficient, clearly say that live data could not be fetched instead of guessing from old knowledge. "
            "You have no tools or function-calling capability. Never attempt to call web.run, a browser, a function, or any other tool. "
            "When the user asks for code, respond with ONLY one clean triple-backtick code block. Put the complete corrected code inside it. "
            "Do not include output, explanation, headings, comments about the code, or any text outside the code block."
        )

        user_content = query
        if web_context:
            user_content = (
                f"User question: {query}\n\n"
                f"Live web context:\n{web_context}\n\n"
                "Answer in a short, clear way. Mention that it is based on live search results."
            )

        model = get_groq_model()
        print(f"Using Groq model: {model}")
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]
        try:
            response = client.chat.completions.create(model=model, messages=messages)
        except Exception as exc:
            if not is_tool_use_error(exc):
                raise

            fallback_model = get_groq_model(excluded_models=[model])
            print(f"Model {model} attempted a tool call; retrying with {fallback_model}")
            response = client.chat.completions.create(model=fallback_model, messages=messages)

        reply = response.choices[0].message.content

        if is_current_info_request(query) and not is_code_request(query) and not web_context:
            reply = "I could not fetch live current data right now. Please check your internet connection and try again."

        if is_code_request(query):
            reply = format_code_reply(reply, query)

        print(reply)
        return reply

    except Exception as exc:
        # Return a message so the UI does not appear stuck when the AI request fails.
        error_name = type(exc).__name__
        error_text = str(exc).lower()
        print(f"Groq AI request failed ({error_name}): {exc}")

        if "authentication" in error_name.lower() or "api key" in error_text or "invalid api key" in error_text:
            return "AI key is invalid or expired. Add a new GROQ_API_KEY in the .env file, then restart Jarvis."
        if "rate" in error_name.lower() or "rate limit" in error_text or "429" in error_text:
            return "AI is temporarily rate-limited. Please wait a moment and try again."
        if "model_not_found" in error_text or "does not exist" in error_text or "do not have access" in error_text:
            return "The configured AI model is unavailable. Remove GROQ_MODEL from .env and restart Jarvis so it can select an available model automatically."
        if "connection" in error_name.lower() or "timeout" in error_text or "network" in error_text:
            return "Jarvis could not reach the AI service. Check your internet, firewall, or proxy connection and try again."
        return "AI request failed. Please check the Jarvis console for the detailed error and try again."

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
