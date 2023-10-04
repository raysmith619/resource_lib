# speech_maker_cmd.py 03Oct2023  crs 
"""
Speach command
TBD - independant control of speach engine properties
"""

class SpeechMakerCmd:
    """ Command to execute
    """

    def __init__(self, cmd_type=None, msg=None, msg_type=None,
                 rate=None, volume=None):
        """ Setup command
        :cmd_type: command to execute
                "MSG" - speak message
                "CLEAR" - clear pending speech
                "QUIT" - quit operation
        :msg: text to speak SpeakText
        :msg_type: type of message
                REPORT: std reporting
                CMD: command
                ECHO: echo of user input
            default: REPORT
        :rate: speech rate default: 240
        :volume: speech volume default: .9
        """
        self.cmd_type = cmd_type
        self.msg = msg
        self.msg_type = msg_type
        if rate is None:
            rate = 240
        self.rate = rate
        if volume is None:
            volume = .9
        self.volume = volume

    def __str__(self):
        ret = f"SpeechMakerCmd {self.cmd_type}"
        if self.msg is not None:
            ret += f" {self.msg}"
        if self.msg_type is not None:
            ret += f" {self.msg_type}"
        return ret
