 

import os
import sys


def useAppDirectory():
        if getattr(sys, "frozen", False):
                os.chdir(os.path.dirname(sys.executable))
        else:
                os.chdir(os.path.dirname(os.path.abspath(__file__)))


def startJarvis():
        print("Process 1 is running.")
        from main import start
        start()


if __name__ == '__main__':
        useAppDirectory()
        startJarvis()
        print("system stop")
