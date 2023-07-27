# text_to_speech_cmd.py     26Jul2023  crs
"""
Text to speech commands
"""
class TextToSpeechCmd:
    def __init__(self, msg=None, msg_type="REPORT",
                   rate=240, volume=.9, wait=True, cmd_type=None):
        self.msg = msg
        self.msg_type = msg_type
        self.rate = rate
        self.volume = volume
        self.wait = wait
        self.cmd_type = cmd_type

    def __str__(self):
        st = "TextToSpeechCmd:"
        st += self.msg
        st += f" {self.msg_type}"
        st += f" rate={self.rate}"
        st += f" volume={self.volume}"
        st += f" wait={self.wait}"
        st += f" cmd_type={self.cmd_type}"
        return st
    
class TextToSpeechResult:
    RES_OK = "RES_OK"
    RES_ERR = "RES_ERR"
    def __init__(self, msg=None, cmd_type=None,
                 code=None):
        if code is None:
            code = self.RES_OK
        self.msg = msg
        self.cmd_type = cmd_type
        self.code = code
