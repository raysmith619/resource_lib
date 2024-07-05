#pyttsx_events.property
""" Looking at events
"""
import pyttsx4 as pyttsxN

engine = pyttsxN.init()
def onStart(name):
    print('starting', name)
def onWord(name, location, length):
    print('word', name, location, length)
def onEnd(name, completed):
    print('finishing', name, completed)
    if name == 'fox':
        engine.say('What a lazy dog!', 'dog')
    elif name == 'dog':
        engine.endLoop()

engine = pyttsxN.init()
engine.connect('started-utterance', onStart)
engine.connect('started-word', onWord)
engine.connect('finished-utterance', onEnd)
engine.say('The quick brown fox jumped over the lazy dog.', 'fox')
engine.startLoop()
