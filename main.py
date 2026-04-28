import os
import eel

from engine.feature import *
from engine.command import*
from engine.auth import recoganize
from engine import pattern_lock

def start():
    eel.init("www")

    playAssistantSound()

    @eel.expose
    def getPatternState():
        return {"is_set": pattern_lock.is_pattern_set()}

    @eel.expose
    def setPattern(pattern):
        return pattern_lock.set_pattern(pattern)

    @eel.expose
    def unlockPattern(pattern):
        return pattern_lock.unlock_pattern(pattern)

    @eel.expose
    def changePattern(current_pattern, new_pattern):
        return pattern_lock.change_pattern(current_pattern, new_pattern)

    @eel.expose
    def removePattern(current_pattern):
        return pattern_lock.remove_pattern(current_pattern)

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
            if pattern_lock.is_pattern_set():
                speak("Draw your pattern to unlock")
                eel.showPatternLock("unlock")
            else:
                speak("Set your pattern lock")
                eel.showPatternLock("setup")
        else:
            speak("Face Authentication fail")



    os.system('start msedge.exe --app="http://localhost:8000/index.html"')

    eel.start('index.html', mode=None, host='localhost', block=True)
