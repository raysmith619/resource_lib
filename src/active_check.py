# active_check.py
"""
active resource check

Facilitate verification and activity surrounding
resources such as windows which may, when destroyed,
preclude proper activity of some code.
Developed to avoid problems with functions which
may be called after resources, such as windows,
are destroyed asynchronously.
"""
class ActiveCheck():
    active = True       # Overall - overrides non-actives
    non_actives = {}        # Individual, by name
    
    @classmethod
    def set_active(cls, name=None):
        """ Set / reset as active
        """
        if name is None:
            cls.active = True
            cls.non_actives = {}    # Clear not actives
        else:
            if name in cls.non_actives:
                del cls.non_actives[name]
    
    @classmethod
    def clear_active(cls, name=None):
        """ Clear / disable as active
        """
        if name is None:
            cls.active = False
            cls.non_actives = {}    # Clear not actives
        else:
            cls.non_actives[name] = True


    @classmethod
    def is_active(cls, name=None):
        """ Test if active
        """
        if not cls.active:
            return False        # Overall
        
        if name is not None and name in cls.non_actives:
            return False    # This name is not active
        
        return True
    


    @classmethod
    def not_active(cls, name=None):
        """ Test if active
        """
        return not cls.is_active(name)

            
    
if __name__ == "__main__":
    from select_trace import SlTrace
    
    def a():
        SlTrace.lg("a")
        if ActiveCheck.not_active("a"):
            return
        
        SlTrace.lg("a-active")
        
    def b():
        SlTrace.lg("b")
        if ActiveCheck.not_active("b"):
            return
        
        SlTrace.lg("b-active")
        a()
        
    def c():
        SlTrace.lg("c")
        a()
        b()
        clr_tag = "a"
        SlTrace.lg("clearing %s" % clr_tag)
        ActiveCheck.clear_active(clr_tag)
        a()
        b()
        clr_tag = "b"
        SlTrace.lg("clearing %s" % clr_tag)
        ActiveCheck.clear_active(clr_tag)
        clr_tag = "b"
        SlTrace.lg("setting %s" % clr_tag)
        ActiveCheck.set_active(clr_tag)
        a()
        b()
        clr_tag = "a"
        SlTrace.lg("setting %s" % clr_tag)
        ActiveCheck.set_active(clr_tag)
        a()
        b()
        clr_tag = None
        SlTrace.lg("clearing %s" % clr_tag)
        ActiveCheck.clear_active(clr_tag)
        a()
        b()
    
    SlTrace.lg("Test Begin")
    c()
    SlTrace.lg("End of Test")
