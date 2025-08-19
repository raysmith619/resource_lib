#name_to_obj.py 10Aug20Aug2025  crs
""" Associate a unique name, e.g., setting to object
"""

class NameToObj:
    def __init__(self, dict=None):
        self.dict = dict
        
        
    def set_dict(self, dict):
        """ Setup dictionary of objects
        :dict: dictionary, by name, of objects
        """
        self.dict = dict
        
    
    