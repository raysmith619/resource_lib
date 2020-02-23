# select_valueition.py
"""
Object position
relative to containing object
"""

class SelectPosition:
    def __init__(self, value=None):
        if value is None:
            value = [0.,0.]
        self.value = value


    def get(self):
        return self.value

    def get_x(self):
        return self.value[0]
    
    def get_y(self):
        return self.value[1]
    
        
    def set(self, value):
        """ Set valueition
        :value: valueition
        """
        self.value = value
       
    
    def set_x(self, x):
        self.value[0] = x
        
    
    def set_y(self, y):
        self.value[1] = y
        
    
    def set_xy(self, x, y):
        self.value = [x,y]
        
    