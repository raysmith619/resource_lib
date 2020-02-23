# select_message.py


class SelectMessage:
    def __init__(self, text, color=None,
                      font_size=None,
                      time_sec=None,
                      msg=None):
        """ Setup select message
        """
        self.text = text
        self.msg = msg
        if color is None:
            color = "dark gray"
        self.color = color
        self.font_size = font_size
        self.time_sec = time_sec
        self.end_time = None        # time to end if another
        
    def __str__(self):
        """ Informative string
        """
        st = self.text + " " + self.color
        if self.time_sec is not None:
            st += " %.2f sec" % self.time_sec
        return st

    def destroy(self):
        if self.msg is not None:
            self.msg.destroy()
        self.msg = None
            