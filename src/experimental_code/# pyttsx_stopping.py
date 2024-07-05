# pyttsx_stopping.py    25Aug2023  crs from
""" Stopping current talking
"""
import multiprocessing
import pyttsx4 as pyttsxN
import time
from threading import Thread


def threaded(fn):
    def wrapper(*args, **kwargs):
        thread = Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper

def speak(phrase):
    engine = pyttsxN.init()
    engine.say(phrase)
    engine.runAndWait()
    engine.stop()

def stop_speaker():
    global term
    term = True
    t.join()

@threaded
def manage_process(p):
	global term
	while p.is_alive():
		if term:
			p.terminate()
			term = False
		else:
			continue

	
def say(phrase):
	global t
	global term
	term = False
	p = multiprocessing.Process(target=speak, args=(phrase,))
	p.start()
	t = manage_process(p)
		
if __name__ == "__main__":
	say("this process is running right now")
	time.sleep(1)
	stop_speaker()
	say("this process is running right now")
	time.sleep(1.5)
	stop_speaker()
 