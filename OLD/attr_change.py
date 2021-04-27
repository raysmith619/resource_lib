#attr_change.py    22Mar2021  crs
"""
Changing Attributes
e.g. colors, shapes for keyboard_draw.py 
attributes change constant, ascending, descending, random
"""
import random

class Attribute:
    
    changes_values = {"ascending",
                      "constant",
                      "descending",
                      "random"
                      }

    @classmethod
    def _is_changes_value(cls, val):
        return val in cls.changes_values
    
    def __init__(self, name, values, changes="ascending",
                 index=None ):
        self.name = name
        self.values = values
        self.changes = changes
        if index is None:
            if changes == "ascending":
                index = -1
            elif changes == "descending":
                index = 0
        self.index = index
        self.save_settings()
        self.reset()

    def add_value(self, value, index=None):
        """ add value to list at index
        :value: value to add
        :index: position to add
                default: beginning (0)
        :returns: value
        """
        if index is None:
            index = 0
        self.values.insert(index, value)
        return value
        
    def is_changes_value(self, val):
        return Attribute._is_changes_value(val)

        
    def reset(self):
        """ Reset to initial settings
        """
        self.restore_settings()
        '''
        if self.changes == "ascending":
            self.index = -1     # Bump to 0
        else:
            self.index  =  0
        '''

    def restore_settings(self):
        self.name = self.orig_settings["name"]
        self.values = self.orig_settings["values"]
        self.changes = self.orig_settings["changes"]
        self.index = self.orig_settings["index"]
        
    def save_settings(self):
        self.orig_settings = {
            "name" : self.name,
            "values" : self.values[:],
            "changes" : self.changes[:],
            "index" : self.index,
            }

    def get_next_value(self, changes=None, index=None):
        """ get next value based on changes
        :changes: next value rule from list
                constant: same value from last
                ascending: next value from list
                descending: prev value from list
                random: random value from list
                        excluding current value
            default: use self.changes
        :index: get this index
                default: use self.index
        """  
        if index is not None:
            self.index = index
            return self.values[index]
        
        if changes is None:
            changes = self.changes
        self.changes = changes
        index = self.index
        nvalue = len(self.values)
        if changes == "constant":
            pass
        elif changes == "ascending":
            index += 1
            if index >= nvalue:
                index = 0
        elif changes == "descending":
            index -= 1
            if index < 0:
                index = nvalue-1
        elif changes == "random":
            chg = random.randint(1, len(self.values)-1)
            index = (index + chg) % len(self.values)
        else:
            raise SelectError(f"Unexpected change spec: {changes}")
        
        if index < 0 or index >= len(self.values):
            index = 0
        self.index = index
        return self.values[index]
    
    
    def get_changes(self):
        """ Get attribute changes value
        """
        return self.changes
    
    def get_name(self):
        """ Get attribute name
        """
        return self.name
    
    def get_index(self):
        """ Get attribute changes value
        """
        return self.index
    
    def get_values(self):
        """ Get attribute values in presentation order
        """
        return self.values

    def set_next_change(self, changes=None):
        """ Set changes - what next brings
        """
        self.changes = changes
    
    
class AttrChange:
    
    def __init__(self):
        """ Setup attribute change
        """
        self.attrs = {}
    
    def add_attr(self, attr):
        """ Add new attribute to change group
        """
        self.attrs[attr.name] = attr

    def add_value(self, name, value, index=None):
        """ add value to att at index
        :name: attribute name
        :value: value to add
        :index: position to add
                default: beginning (0)
        :returns: value
        """
        if name not in self.attrs:
            raise SelectError(f"attr name({name} is not in {self.attrs}")
        
        attr = self.attrs[name]
        return attr.add_value(value=value, index=index)

    def get_attr(self, name):
        """ Get attr, given name
        :name: attribute name
        :returns: Attribute for name, if one
                    None if none
        """
        if name in self.attrs:
            return self.attrs[name] 
        
        return None
           
    def get_attr_names(self):
        """ Get list of attr names
        """
        return list(self.attrs)
    
    def get_next(self, name, changes=None, index=None):
        """ Get next of this attribute
        :name: attribute name
        :changes: changes
                default: use attribute's changes
        :index: get specified attribute's value at index
        """
        if name not in self.attrs:
            raise SelectError(f"attr name({name} is not in {self.attrs}")
        
        attr = self.attrs[name]
        return attr.get_next_value(changes=changes, index=index)

    def get_next_change(self, name):
        """ Get attribute change value, e.g. constant, ascending, ...
        :name: attribute name
        :return: attribute change setting
        """
        if name not in self.attrs:
            raise SelectError(f"attr name({name} is not in {self.attrs}")

        attr = self.attrs[name]        
        return attr.changes

    def reset(self):
        """ Reset all attr to initial settings
        """
        for attr in self.attrs.values():
            attr.reset()


    def set_next_change(self, name=None, changes=None):
        """ set attribute changes
        :attr: attribute name
        :changes: attribute value
        """
        if name not in self.attrs:
            raise SelectError(f"attribute name({name} is not in {self.attrs}")

        attr = self.attrs[name]
        if not attr.is_changes_value(changes):
            raise SelectError(f"attribute changes {changes}"
                              f" is not in {self.changes_values}")
                    
        attr.set_next_change(changes=changes)

            
if __name__ == "__main__":
    from select_trace import SlTrace
    from select_error import SelectError
    
    atc = AttrChange()
    attr = Attribute("color", 
        ["red", "orange", "yellow", "green",
            "blue", "indigo", "violet"])
    atc.add_attr(attr) 
    attr = Attribute("shape", 
        ["line", "square", "triangle", "circle"],
         changes="random")
    atc.add_attr(attr) 

    nrun = 0        # Test run
    def test_attr(name):
        """ Test/exercise attribute
        :name: attribute name
        """
        global nrun
        nrun += 1
        SlTrace.lg(f"\n{nrun:3} Testing Attribute: {name}")
        attr = atc.get_attr(name)
        SlTrace.lg(f"  {attr.get_name()}:"
                   f"  changes: {attr.get_changes()}"
                   f"  index: {attr.get_index()}")
        atc.add_value(name=name, value=f"{name}_test_value_{nrun}")
        values = attr.get_values() 
        SlTrace.lg(f"values: {values}")
        for n in range(len(values)*3):
            SlTrace.lg(f"  {n}: {atc.get_next(name)}"
                       f"  index: {attr.get_index()}")
        
    attr_names = atc.get_attr_names()
    SlTrace.lg(f"\nattributes: {attr_names}")
    for attr_name in attr_names:
        test_attr(attr_name)

    SlTrace.lg("\nResetting Attributes")
    atc.reset()
    for attr_name in attr_names:
        test_attr(attr_name)
        