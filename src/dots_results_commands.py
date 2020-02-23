# dots_results_commands.py
"""
Results file commands
See dots_game_file.py for game and file layout
    
    File Format (Customized to be a small subset of python
                to ease processing flexibility)
     """
import sys, traceback
import re
import os
from pathlib import Path
from datetime import date

from select_trace import SlTrace
from select_error import SelectError


class SkipFile(Exception):
    """ Raised to skip current file
    """
    pass

class DotsResultsCommands:
    """ The hook from commands expressed via python command files to 
    the frame worker
    Make it an "ALL CLASS" to ease access via file based calls
    """
    
    @classmethod
    def get_loader(cls):
        if not hasattr(cls, "loader"):
            return None
        
        return cls.loader

    @classmethod    
    def set_loader(cls, loader):
        """ Set command loader object for file based commands
        :loader: loading object for commands
        """
        cls.loader = loader
        
    def __init__(self):
        """ Setup command action functions
        :loader:  loader object
        """
        self.set_loader(None)


"""
language functions - found in game files
See definitions in member functions

language commands
"""

def version(version_str, **kwargs):
    return DotsResultsCommands.get_loader().version(version_str, **kwargs)

def history(history_str, **kwargs):
    return DotsResultsCommands.get_loader().history(history_str, **kwargs)

def pgm_info(info_str, **kwargs):
    return DotsResultsCommands.get_loader().pgm_info(info_str, **kwargs)
    
    
def game(*args, **kwargs):
    return DotsResultsCommands.get_loader().game(*args, **kwargs)


def moves(*args, **kwargs):
    return DotsResultsCommands.get_loader().moves(*args, **kwargs)


def results(*args, **kwargs):
    return DotsResultsCommands.get_loader().results(*args, **kwargs)


        
if __name__ == "__main__":
    from dots_game_load import DotsGameLoad
    rC = DotsResultsCommands()
    rF = DotsGameLoad(file_dir=r"..\test_gmres")
    rC.set_loader(rF)
    ###from dots_game_load import *
    # C:\Users\raysm\workspace\python\crs_dots\test_gmres\dotsgame_20190902_102335.gmres
    # On: September 02, 2019
    exec(r"""
version("ver01_rel01")
game(name="test1", nplayer=2, nrow=7, ncol=7, nmove=4, ts="20190902_102335")
moves((1,2,2), (2,2,3), (1,3,4), (2,3,4))
results((1,2), (2,5))

game(name="test2", nplayer=2, nrow=5, ncol=7, nmove=4, ts="20190902_102335")
moves((1,2,3), (2,2,4), (1,3,5), (2,3,6))
results((1,2), (3,4))

    
SlTrace.lg("%d games in %d files" % (rF.get_num_games(), rF.get_num_files()))
    """)        
