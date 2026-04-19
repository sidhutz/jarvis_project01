import pyttsx3
import speech_recognition as sr
import eel
import time
from cloud import save_chat

def speak(text, speak_flag=False):
    text = str(text)

    # detect code block
    is_code = "```" in text

    eel.DisplayMessage(text)
    eel.receiverText(text, is_code)

    if speak_flag:
        engine = pyttsx3.init('sapi5')
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[0].id)
        engine.setProperty('rate', 174)
        engine.say(text)
        engine.runAndWait()

    try:
        eel.hideThinking()
    except:
        pass



def takecommand():
    r = sr.Recognizer()

    with sr.Microphone() as source:
        print('listening...')
        eel.DisplayMessage('listening...')
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source)

        audio = r.listen(source, 10, 6)

    try:
        print('recognizing...')
        eel.DisplayMessage('recognizing....')
        query = r.recognize_google(audio, language='en-in')
        print(f"user said:{query}")
        eel.DisplayMessage(query)
       
        
    except Exception as e:
        return ""
    
    return query.lower()

@eel.expose
def loadHistory():
    from cloud import get_history
    data = get_history()
    print("HISTORY DATA:", data) 
    return data

@eel.expose
def allCommands(message = 1):

    if message == 1:
        query = takecommand()
        print(query)
        eel.senderText(query)

    else:
        query = message
        eel.senderText(query)

    try:

        if "open" in query:
            from engine.feature import openCommand
            openCommand(query)

        elif "on youtube" in query:
            from engine.feature import PlayYoutube
            PlayYoutube(query)

        elif "search" in query or "google" in query:
            from engine.feature import searchGoogle
            searchGoogle(query)

        elif "remember" in query:
            from engine.feature import rememberSomething
            rememberSomething(query)

        elif "what is" in query:
            from engine.feature import recallMemory
            recallMemory(query)

        elif "weather" in query:
            from engine.feature import getWeather
            getWeather("lucknow")

        elif "send message" in query or "phone call" in query or "video call" in query:
            from engine.feature import findContact, whatsApp, makeCall
            contact_no, name = findContact(query)

            if(contact_no != 0):
                speak("Which mode you want to use whatsapp or mobile")
                preferance = takecommand()
                print(preferance)

                if "mobile" in preferance:
                    if "send message" in query or "send sms" in query:
                        speak("what message to send")
                        message = takecommand()

                    elif "phone call" in query:
                        makeCall(name, contact_no)

                    else:
                        speak("please try again")

                elif "whatsapp" in preferance:
                    message = ""

                    if "send message" in query:
                        message = 'message'
                        speak("what message to send")
                        query = takecommand()

                    elif "phone call" in query:
                        message = 'call'

                    else:
                        message = 'video call'

                    whatsApp(contact_no, query, message, name)

       
        else:
            from engine.feature import chatBot
            from cloud import save_chat

            reply = chatBot(query)

            if reply:
                speak(reply)
                save_chat("sidhu", query, reply)

    except Exception as e:
        print("error:", e)

    eel.ShowHood()


