# display_tracking.py    17-Feb-2020  crs
"""
Tracking canvas display by part id
"""
from select_trace import SlTrace
from active_check import ActiveCheck

class DisplayTracking():
    
    def __init__(self, game_control):
        """ Setup connection to board
        """
        self.game_control = game_control
        self.displayed_objects_by_id = {}   # dictionary, by id, of lists of obj of lists/lists of lists
        self.displayed_tags_by_id = {}      # dictionary, by id, of lists of tags /lists of lists

    def add_display_objects(self, part, objects):
        """ Add newly displayed objects on canvas
        :part: displaying part
        :objects: objects, or lists of objects, or lists of...
        """
        dos = self.get_displayed_objects(part)
        dos.append(objects)

    def add_display_tags(self, part, tags):
        """ Add tags of newly displayed canvas objects
        :part: displayed part
        :tags: tag, or lists of tags, or lists of...
        """
        dts = self.get_displayed_tags(part)
        dts.append(tags)

    def get_displayed_objects(self, part):
        """ get / create pointer to part's displayed objects
        :part: displayed part
        Create empty list if not already present
        """
        if part.part_id not in self.displayed_objects_by_id:
            self.displayed_objects_by_id[part.part_id] = [] # Start empty list
        pdos = self.displayed_objects_by_id[part.part_id]
        return pdos

    def get_displayed_tags(self, part):
        """ get / create pointer to part's displayed tags
        :part: displayed part
        Create empty list if not already present
        """
        if part.part_id not in self.displayed_tags_by_id:
            self.displayed_tags_by_id[part.part_id] = []     # Start empty list
        pdts = self.displayed_tags_by_id[part.part_id]
        return pdts
        
    
        
    def display_clear(self, part, display=False):
        """ Clear out display of current edge
        :part: displayed part
        ;display: True - update display, default: no update
        """
        if ActiveCheck.not_active():
            return      # At end
        
        if self.game_control.area is None:
            return
        
        if self.game_control.area.canvas is None:
            return
        
        if part.part_id not in self.game_control.area.parts_by_id:
            SlTrace.lg(f"part {part} not in parts_by_id")

        self.delete_objects(part)
        self.delete_tags(part)
        if display:
            self.game_control.area.mw.update()

    def delete_objects(self, part, objs=None, quiet = False):
        """ Delete objects or list of objects
        :part: part displayed default: just delete objs
        :objs: object or list of lists of objects
                default: use parts display objects
        :quiet: suppress tracing
        """
        if objs is None and part is not None:
            objs = self.get_displayed_objects(part)
        if objs is None:
            return
        
        if not quiet and SlTrace.trace("delete_objects"):
            SlTrace.lg(f"delete_objects: {part} objects:{objs}")
        
        if isinstance(objs, list):
            for obj in objs:
                if not quiet and SlTrace.trace("delete_objects"):
                    SlTrace.lg(f"delete_object:{part} object: {obj}")
                self.delete_objects(None, obj)
        else:
            objs.destroy()
        if part is not None:        # Top of loop
            del self.displayed_objects_by_id[part.part_id]    # Remove entry
        
    def delete_tags(self, part, tags=None, quiet = False):
        """ Delete tag or list of tags
        :part: part displayed default: just delete tags
        :tags: tag or list of lists of tags default: user part's tags
        :quiet: suppress tracing
        """
        if tags is None:
            if part is not None:
                tags = self.get_displayed_tags(part)
        if tags is None:
            return
        
        if not quiet and SlTrace.trace("delete_tags"):
            SlTrace.lg(f"delete_tags: {self} tags:{tags}")
        
        if isinstance(tags, list):
            for tag in tags:
                self.delete_tags(None, tag, quiet=True)
        else:
            self.game_control.area.canvas.delete(tags)
        if part is not None:        # Top of loop
            del self.displayed_tags_by_id[part.part_id]    # Remove entry


    def set_part(self, part):
        """ Add reference to actual part for reference / conversion
        :part: Part to add to tracking
        """
        self.parts_by_id[part.part_id] = Part
        self.tags_by_id[part.part_id] = []
        part.display_tracking = self        # Augment part with connection to us