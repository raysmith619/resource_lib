# draw_move.py    02Mar2021  crs, cmd structure
"""
Drawing Move
"""
from Lib.shutil import move
""" Marker/Shape info
    for undo / rotate operations
"""
class DrawMove:
    MT_GENERAL = "mt_general"
    MT_MARKER = "mt_marker"
    MT_POSITION = "mt_position"
    MT_ADJUSTMENT = "mt_adjustment"
    
    def __init__(self, drawer, move_type=None,
                 key=None):
        """  Marker/Shape info for undo / rotate operations
        :move_type: General move type
                MT_ADJUSTMENT - current move is to be adjusted
                MT_MARKER - new marker
                MT_POSITION - position move
                MT_GENERAL - general move (unknown)
                default: MT_GENERAL 
        :key: move's text key, if one
        """
        self.drawer = drawer
        self.canvas_tags = []       # Extra canvas tags, if any
        self.draw_markers = []
        self.images = []            # Extra images, if any            
        if move_type is None:
            move_type = DrawMove.MT_GENERAL
        self.move_type = move_type

        def add_marker(self, marker):
            """ Add move's marker
            """
            self.draw_markers.append(marker)
        
        def undo(self):
            """ Undo this move
            """
            
        def redo(self):
            """ do/redo this move
            """
        