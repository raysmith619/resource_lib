# java_properties.py    20Sep2018
"""
Java properties file processing
Simple single name.name.... = value
"""
import os
import sys
import copy
import re

from crs_funs import dot_sorted

class JavaProperties:
    @classmethod
    def snapshot_properties(cls, sn=None,
                                req=None, req_not=False,
                                req_match=None,
                                req_match_not=False):
        """ Properties snapshot, selected by req string and or req_match
        :sn: properties state
            default: REQUIRED
        :req: only keys which have this string
        :req_not: only keys that don't have this string
        :req_match: only keys which match this regular expression
        :req_match_not: only keys which don't match this regex
                
        :returns: (JavaProperties(only in sn1),
                  JavaProperties(sn1, sn1,sn2 differ),
                  JavaProperties(sn2, sn1,sn2 differ),
                  JavaProperties (only in sn2)) tuple
        """
        if req is None and req_match is None:
            return sn.copy()
        
        jp_in_sn = JavaProperties()
        for prop_key in sn.getPropKeys():
            if cls.is_our_key(prop_key, req=req, req_not=req_not, req_match=req_match, req_match_not=req_match_not):
                jp_in_sn.setProperty(prop_key, sn.getProperty(prop_key, None))
        return jp_in_sn



    @classmethod
    def is_our_key(cls, prop_key, req=None, req_not=False, req_match=None, req_match_not=False):
        """ Test if this is our key
        """
        if req is not None:
            if prop_key.find(req) >= 0:
                if req_not:
                    return False                # string found but not wanted - skip it
            else:
                return False                    # Required string not found - skip it
    
        if req_match is not None:
            if re.match(req_match, prop_key) is not None:
                if req_match_not:
                    return False                # string found but not wanted - skip it
            else:
                if not req_match_not:
                    return False                    # Required string not found - skip it
        return True                                 # Our key

    
    def __init__(self, filename=None):
        self.props = {}
        self.filename = None
        if filename is not None:
            self.props = self.load(filename)

    def copy(self):
        """ Copy current properties data snapshot
        elemebts copied to protect from changes to source
        """
        new_copy = JavaProperties()
        for key in self.props:
            new_copy.props[key] = copy.copy(self.props[key])
        return new_copy
                
    def load(self, filename):
        sep = "="
        if "." not in(filename):
            filename += ".properties"   # Default extension
        if not os.path.isabs(filename):
            filename = os.path.abspath(filename)
        self.filename = filename
        if not os.path.exists(filename):
            with open(filename, "w") as fout:
                abs_filename = os.path.abspath(filename)
                print("Creatng empty file %s" % abs_filename)
                print("# %s Empty - created" % filename, file=fout)
                fout.close()
        with open(filename) as fin:
            props = {}
            for line in fin:
                if "#" in line:
                    ic = line.index("#")
                    line = line[ic:]
                if sep not in line:
                    continue
                            # Find the name and value by splitting the string
                name, value = line.split(sep, 1)
    
                # Assign key value pair to dict
                # strip() removes white space from the ends of strings
                props[name.strip()] = value.strip()
        return props

    def getPropKeys(self, startswith=None):
        """ Get list of keys
        :startswith: starting string
            default: All keys
        :returns: keys sorted dot wise (dot_sorted)
        """
        if startswith is None:
            return dot_sorted(self.props.keys())
        
        keys = []
        for key in dot_sorted(self.props.keys()):
            if key.startswith(startswith):
                keys.append(key)
        return keys

    def getPropTree(self, startswith=None):
        """ Get tree based on doted keys
           head.next_sections.....
           :startswith: restrict tree to those keys that start with this string
                           default: all keys
        :returns: a dictionary tree by segment values each containing a dictionary of 
                the subsequent sections, till the bottom leaf.
                a.b.c, a.c, a.d, a.b.c2, b.c2 => {a, b}  a: {b,c,}  b: {c, c2}
                each value will be the 
        """
        tree = {}
        keys = getPropKeys(startswith=startswith)
        for key in keys:
            self.add_key_to_tree(key)
        ### TBD
            
        
        
    def getProperty(self, key, default):
        """ Get property, returning default if none
        """
        try:
            value = self.props[key]
        except:
            value = default
        return value
    
        
    def get_properties(self):
        """ Return dictionary of keys and value text strings
        """
        return self.props


    def hasProp(self, key):
        """ Check if property is already present
        :key: property key
        :returns: True iff property is present
        """
        if key in self.props:
            return True
        
        return False

    def is_empty(self):
        """ Check if no properties
        """
        if len(self.props) == 0:
            return True
        
        return False

    def deleteProperty(self, key):
        """ Delete property(key)
        """
        if self.hasProp(key):
            del self.props[key]


    def setProperty(self, key, value):
        """ Set property(key) value
        Converts value to string before storing
        """
        self.props[key] = str(value)


    def store(self, fp, title=None, keys=None, list_props=True):
        """ Store properties file
        :fp: Output file
        :title: Optional comment line
        :keys: list of property keys to store
                default: self.props
        :list_props: List properties on stdout
        """
        if keys is None:
            keys = self.props.keys()
        try:
            if title is not None:
                print("# %s" % title, file=fp)
            for key in dot_sorted(keys):
                prop_str = f"{key}={self.props[key]}"
                print(prop_str, file=fp)
                if list_props:
                    print(prop_str)
            fp.close()
        except IOError as ioex:
            print("Error in storing Properties file %s" % title)
            print("errno: %d" % ioex.errno)
            print("err code: %d" % ioex.errorcode[ioex.errno])
            print("err message: %s" % os.strerror(ioex.errno))

    
    def get_path(self):
        """ Get full path to properties file
        """
        return self.filename        

    
if __name__ == "__main__":
    propfile = "test"
    pr = JavaProperties(propfile)
    dp = pr.get_properties()
    
    for key in dp:
        print("dp[%s] = %s" % (key, dp[key]))
    
    pr2 = JavaProperties(propfile)
    pk = "new_key"
    default_val = "check_val"
    pval = pr2.getProperty(pk, default_val)
    if pval == default_val:
        print("Got expected default %s value %s" % (pk, pval))
    else:
        print("Got %s NOT the EXPECTED %s" % (pval, default_val))
        print("Quitting")
        sys.exit(1)
        
    new_value = "New VALUE"   
    pr2.setProperty(pk, new_value)
    
    propfile2 = "test2.properties"
    abs_propfile2 = os.path.abspath(propfile2)
    print("\nWriting new properties file %s" % abs_propfile2)    
    with open(propfile2, "w") as p2f:
        pr2.store(p2f, "# %s properties file 2" % propfile2)
        p2f.close()

    print("Loading new properties file %s" % propfile2)    
    pr2b = JavaProperties(propfile2)
    pk2 = pk
    pval2 = pr2b.getProperty(pk2, None)
    if pval2 is None:
        print("Property %s not found" % pk2)
        sys.exit(1)
        
    print("pval=%s" % pval2)
    print("new_value=%s" % new_value)
    if pval2 != pval2:
        print("pval2 Not Equal to pval")
        print("Property key:%s: %s was NOT the EXPECTED %s"
               % (pk2, pval2, pval))
        print("Quitting")
        sys.exit
    print(f"deleting key={pk}")
    if pr2b.hasProp(pk):
        print(f"Before: property {pk} is here")
    pr2b.deleteProperty(pk)
    if not pr2b.hasProp(pk):
        print(f"After: property {pk} is gone")
    if pr2b.hasProp(pk):
        print(f"property {pk} is NOT gone")
    print("End of Test")        
        