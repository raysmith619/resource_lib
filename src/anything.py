#anything.py    09Sep2024  crs
""" Anything - an example of how __getattr__ can be used to provide attributes
on the fly
"""
class Anything():
    """ objects who have any members
    """
    def __init__(self, *args,**kwargs):
        self.args = args            # Save incase we want to use them
        self.kwargs = kwargs
        
    def __getattr__(self, __name, *args, **kwargs):
        def excecute(*args, **kwargs):
            return f"defined on the fly {__name, args, kwargs}"
        
        return excecute
    
    def our_own(self, *args):
        """ Our own function"""
        print("our_own", *args)
    
if __name__ == '__main__':
    ath = Anything()
    
    ath.our_own("predefined")
    
    print(ath.new())
    print(ath.foo('bar'))
    print(ath.any_old_function("with", args="of any type"))

    