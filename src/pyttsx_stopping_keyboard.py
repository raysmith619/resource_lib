# pyttsx_stopping_keyboard.py   25Aug2023 crs
""" Stopping pyttsx3 using keyboard
"""
import multiprocessing
import pyttsx3
import keyboard

def sayFunc(phrase):
    engine = pyttsx3.init()
    engine.setProperty('rate', 160)
    engine.say(phrase)
    engine.runAndWait()

def say(phrase):
	if __name__ == "__main__":
		p = multiprocessing.Process(target=sayFunc, args=(phrase,))
		p.start()
		while p.is_alive():
			if keyboard.is_pressed('q'):
				p.terminate()
			else:
				continue
		p.join()

say("this process is running right now")
