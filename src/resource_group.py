# resource_group.py    crs    02Jan2020
"""
support to handle resource groups
"""
from select_error import SelectError
from select_trace import SlTrace

class ResourceEntry:
    """ Resource group entry
    """
    def __init__(self, obj, name=None, tag=None, desc=None):
        """ Resource Group entry
        :obj: resource object
        :name: Entry unique name, default: entry number
        :tag: Entry tag to facilitate collecting by sub grouping
        :desc: Optional description
        """
        if name is None:
            if isinstance(obj, str):
                name = obj
            else:
                SlTrace.lg(f"object(entry needs a name")
            
        self.obj = obj
        self.name = name
        self.tag = tag
        self.desc = desc
        self.number = None          # Number in group
        
class ResourceGroup:
    """Group of resources to handle
    """
    def __init__(self):
        self.group_dict = {}    # Group dictionary
        self.entry_number = 0   # Grows as entries added
        
    def add(self, entry, name=None, number=None):
        """ Add new entry
        :entry: (ResourceEntry) to be added
            if str - create entry with name as string
        :name: entry's name default:
        :number: entry number (overrides entry's) 
        """
        if number is None:
            next_entry_number = self.entry_number + 1
        else:
            next_entry_number = number
        if isinstance(entry, str):
            entry = ResourceEntry(entry, name=entry)
        if name is not None:
            entry.name = name
        if entry.number is None:
            entry.number = next_entry_number
        if entry.name is None:
            entry.name = f"_{next_entry_number}_"
        if entry.name in self.group_dict:
            raise SelectError(f"add: {entry.name} is already in group")
        
        self.group_dict[entry.name] = entry
        self.entry_number = next_entry_number

    def destroy(self, name):
        """ Destroy member
        If member object has destroy member call it
        :name: member name
        """
        if not name in self.group_dict:
            raise SelectError(f"destroy {name} is not in group")
        
        mem = self.group_dict[name]
        del self.group_dict[name]
        if hasattr(mem.obj, 'destroy'):
            mem.obj.destroy()

    def destroy_all(self):
        """ Destroy all members
        """
        group_names = list(self.group_dict)
        for name in group_names:
            self.destroy(name)
                        
    def remove(self, name):
        """ Remove member, if present
        :returns: member else None
        """
        if not name in self.group_dict:
            return None
        
        mem = self.group_dict[name]
        del self.group_dict[name]
        return mem
    
    def list(self, desc=None):       
        """ List group members
        :desc: description text if any
        """
        if desc is not None:
            SlTrace.lg(desc)
        mems_str = ""
        for name in self.group_dict:
            mem = self.group_dict[name]
            if mems_str != "":
                mems_str += ", "
            mems_str += mem.name
        SlTrace.lg(mems_str)

if __name__ == "__main__":
    class TestObj:
        def __init__(self, *strs):
            self.strs = strs
        
        def __str__(self):
            str_str = ",".join(self.strs)
            return str_str
            
        def destroy(self):
            SlTrace.lg(f"TestObj.destroy:{str(self)}")
            del self.strs
            
    rg = ResourceGroup()
    rg.add("one")
    rg.add("two")
    rg.list("after two")
    rg.add("three")
    rg.list("after three")
    rg.destroy("two")
    rg.list("after delete two")
    mem = rg.remove("one")
    SlTrace.lg(f"removed {mem.name}")
    rg.list("after remove one")
    rg.add("four")
    rg.list("after add four")
    rg.destroy_all()
    rg.list("after destroy_all")
    rg.add(ResourceEntry(TestObj("a", "b", "c")), name="abc")
    rg.list("after add abc")
    rg.add(ResourceEntry(TestObj("d", "e", "f"), name="def"))
    rg.list("after add def")
    rg.destroy("abc")
    rg.list("after destroy abc")
    rg.add(ResourceEntry(TestObj("g", "h", "i"), name="ghi"))
    rg.list("after add ghi")
    rg.destroy_all()
    rg.list("after destroy_all")
    SlTrace.lg("End Test")
                