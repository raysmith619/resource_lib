# canvas_tracked.py
"""
Debugging aid to track one or more items added to a canvas
CanvasTracked objects are substitutable for canvas objects
CanvasTracked keeps record of the allocation and deletion of such ObjectsTestCase
"""
from tkinter import *
import traceback

from select_trace import SlTrace
from select_error import SelectError
    
class CanvasTracked(Canvas):
    track_no = 0        # Unique element tracking number
    
    def __init__(self, master=None, cnf={}, parts_control=None, **kw):
    ###def __init__(self, master, name, *args, **kwargs):
        """ Set up canvas object tracking
        :master: canvas to be is_tracked
        :parts_control: parts info (e.g. SelectDots)
        """
        ###super(Canvas, self).__init__(master=master, cnf=cnf, **kw)
        Canvas.__init__(self, master=master, cnf=cnf, **kw)
        self.by_rec_id = {}
        self.by_track_no = {}
        self.start_track_no = CanvasTracked.track_no
        self.parts_control = parts_control

    def set_game_control(self, game_control):
        """ Connect with game control to allow info access
        """
        self.game_control = game_control

    def set_parts_control(self, parts_control):
        """ Connect with parts control to allow info access
        """
        self.parts_control = parts_control
         
    def set_start_track(self, num):
        """ Set tracking start number
        :num: number to start searching/listing
            default: current track no
        """
        if num is None:
            num = CanvasTracked.track_no
        self.start_track_no = num

 
    def get_start_track(self):
        """ Return current tracking start
        """
        return self.start_track_no
    
           
    def create_rectangle(self, *args, **kwargs):
        """ Track rectangles CREATED
        """
        rec_id = super().create_rectangle(*args, **kwargs)
        self.track_no = self.new_track_no()
        call_stack = traceback.extract_stack()
        track = (rec_id, self.track_no, call_stack)
        self.by_track_no[self.track_no] = self.by_rec_id[rec_id] = track
        return rec_id

    def delete(self, rec_id):
        """ delete id/tag
        """
        if rec_id in self.by_rec_id:
            track = self.by_rec_id[rec_id]
            del self.by_rec_id[rec_id]
            track_no = track[1]
            del self.by_track_no[track_no]
        super().delete(rec_id)


    def get_part(self, id=None, type=None, sub_type=None, row=None, col=None):
        """ Get basic part
        :id: unique part id
        :returns: part, None if not found
        """
        if self.parts_control is None:
            raise SelectError("get_part can't function because parts_control not set")
        return self.parts_control.get_part(id=id, type=type, sub_type=sub_type, row=row, col=col)


    def get_tracked(self, start=None, part=None):
        """ Get tracked entries starting at start
        :start: starting number
                default: start_track_no
        :part: part/id Track this part/id
                default: All parts
        """
        if start is None:
            start = self.start_track_no
        if part:
            if isinstance(part, int):
                part_id = part 
            else:
                part_id = part.part_id
        else:
            part_id = None
            
        tracks = []
        for track in list(self.by_track_no.values()):
            rec_id, track_no, call_stack = track
            if track_no >= start:
                if part_id:
                    track_rec_id = rec_id
                    track_part_id = self.get_part_id(track_rec_id)
                    if track_part_id and part_id == track_part_id:
                        tracks.append(track)
                else:
                    tracks.append(track)
                    
        return tracks 


    def trace_item(self, rec_id=None, track_no=None, prefix="", begin=-3, end=-1):
        """ Trace(list) entry
        :rec_id: record id
        :trac_no: tracing number
        :begin: start stack list (-99 99 most recent entries)
        :end: end stack list (-1 most recent entry)
        """
        if rec_id is not None:
            if rec_id in self.by_rec_id:
                track = self.by_rec_id[rec_id]
            else:
                return          # Ignore if not tracked
            
        elif track_no is not None:
            if track_no in self.by_track_no:
                track = self.by_track_no[track]
            else:
                return          # Ignore if not tracked
            
        else:
            raise("trace_item has neither rec_id nor track_no")
        rec_id = track[0]
        tags = self.gettags(rec_id)
        track_no = track[1]
        stack = track[2]
        entries = traceback.format_list(stack)

        # Remove the last two entries for the call to extract_stack() and to
        # the one before that, this function. Each entry consists of single
        # string with consisting of two lines, the script file path then the
        # line of source code making the call to this function.
        ###del entries[-2:]
        part = self.get_part_from_tags(tags)
        SlTrace.lg("%s%s %s %s" % (prefix, rec_id, tags, part))
        for entry in entries[begin:end]:
            SlTrace.lg("%s" % (entry))

    def get_part_from_tags(self, tags):
        for tag in tags:
            if tag.startswith("part:"):
                match = re.search(r'id:(\d+)', tag)
                if match:
                    part_id = int(match.group(1))
                    return self.get_part(part_id)
        return None
    
    
    def get_part_id(self, rec_id=None):
        if rec_id is None:
            raise SelectError("rec_id: Missing trackno")
        tags = self.gettags(rec_id)
        part = self.get_part_from_tags(tags)
        if part:
            return part.part_id
        
        return None
            
        
    def new_track_no(self):
        CanvasTracked.track_no += 1
        return CanvasTracked.track_no
    
    