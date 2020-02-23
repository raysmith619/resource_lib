# select_rotation.py
"""
Object rotation in degrees (counter clockwise)
relative to containing object
"""

class SelectRotation:
    def __init__(self, value=None):
        if value is None:
            value = 0.
        self.value = value


    def get(self):
        return self.value
    
        
    def set(self, value):
        """ Set velocity
        :value: velocity
        """
        self.value = value
        
    