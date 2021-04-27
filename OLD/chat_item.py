#chat_item.py    12Dec2020  crs
"""
Item in a chat sequence
"""
from datetime import datetime

class ChatItem:
    def __init__(self, text=None, time=None, from_name=None, to_name=None):
        """ Initialize chat item_sep
        :text: text of message
        :time: date/time of message default: now
        :from_name: sender of message
        :to_name: destination of message default: me
        """
        self.text = text
        if time is None:
            time = datetime.now()
        self.time = time
        self.from_name = from_name
        self.to_name = to_name
        