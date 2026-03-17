import os
import eel

from engine.feature import *
from engine.command import*
from engine.auth import recoganize

def start():
    eel.init("www")

    playAssistantSound()
    @eel.expose
    def init():
        subprocess.call(r'device.bat')
        eel.hideLoader()
        speak("Ready for face Authentication")
        flag = recoganize.AuthenticateFace()
        if flag == 1:
            eel.hideFaceAuth()
            speak("Face Authentication Successful")
            eel.hideFaceAuthSuccess()
            speak("Hello, Sidhu how can I help you")
            eel.hideStart()
        else:
            speak("Face Authentication fail")



    os.system('start msedge.exe --app="http://localhost:8000/index.html"')

    eel.start('index.html', mode=None, host='localhost', block=True)