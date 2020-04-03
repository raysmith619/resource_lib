# select_trace.py
"""
trace/logging package
modeled after smTrace.java

Debug Tracing with logging support
"""
import re
import os
import atexit

from datetime import datetime
import sys
import traceback

from select_error import SelectError
from java_properties import JavaProperties
###from test.support import change_cwd

"""
Facilitate execution tracing / logging of execution.
 
@author raysmith
"""
class SelectErrorInput(Exception):
    """ Input conversion error
    """
    pass

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise SelectError('Not a recognized Boolean value %s' % v)

    
def str2val(string, value_or_type):
    """ Convert string to value of type default
    :value_type: default value if string is None or variable type
            used as type expected
    :returns: converted value
            throws SelectErrorInput if conversion error
    """
    try:
        if isinstance(value_or_type, str) or value_or_type is str:
            return string
    
        if isinstance(value_or_type, bool) or value_or_type is bool:
            return str2bool(string)
            
        if isinstance(value_or_type, int) or value_or_type is int:
            return int(float(string))       # Treat floats as ints
        
        if isinstance(value_or_type, float) or value_or_type is float:
            return float(string)
    except Exception:
        ###SlTrace.lg(f"=>str2val input {string} error for type:{type(value)}")
        pass
    
    raise SelectErrorInput(f"str2val input {string} error for type:{type(value_or_type)}")

class TraceError(Exception):
    """Base class for exceptions in this module."""
    pass

class SlTrace:
    traceFlagPrefix = "traceFlag"

    """
    Logging Support
    """
    propName = None     # Properties file name None - use script base name
    newExt = None       # if not None => output will have newExt extension
    update = True       # True => write out updated properties at end (save_propfile)     
    propPathSaved = None   # Actual saved path, if saved
    logName = None # Logfile name
    logExt = "sllog" # Logfile extension (without ".")
    started = False     # Set True when logging is started
    closed = False      # Set True when log file is closed
    logWriter = None
    logToScreen = True # true - log, additionally to STDOUT
    stdOutHasTs = False # true - timestamp prefix on STDOUT
    lgsString = "" # Staging area for lgs, lgln
    traceObj = None
    decpl = 0       # Decimal places in time stamp
    defaultProps = None # program properties
    traceAll = False # For "all" trace
    traceFlags = {} # tracing flag/levels
    recTraceFlags = {} # recorded
    mem_used = 0        # Memory used as of last getMemory call
    mem_used_change = 0 # Memory change as of last getMemory call   
    runningJob = True

    @classmethod
    def setup(cls):
        dummy = 0
    
    @classmethod
    def tr(cls, flag, level=1):
    
        cls.setup()        # Insure connection
        return cls.tr1(flag, level=level)

    @classmethod
    def clearFlags(cls):
        """ Clear all trace flags
        """
        cls.traceFlags = {}        # <String, Integer>
        cls.traceAll = 0        # For "all" trace

    
    """
    Setup trace flags from string of the form flag1[=value][,flagN=valueN]* Flags
    are case-insensitive and must not contain ",". Values are optional and
    default to 1 if not present.
    """
    @classmethod
    def setFlags(cls, settings):
        cls.setup() # Insure access
        pat_flag_val = re.compile(r"(\w+)(=(\d+),*)?")
        sets = re.findall(pat_flag_val, settings)
        for setting in sets:
            flag, value = setting[0], setting[2]
            if value is None or value == '':
                value = 1        # Defaule value if no =
            cls.setLevel(flag, value)


    @classmethod
    def setLogExt(cls, logExt):
        """ Setup Logging file default extension This extension is used if no extension
        is provided by user
        """
        cls.logExt = logExt


    @classmethod
    def setLogName(cls, logName):
        """ Setup Logging file name Name without extension is appended with
            "_YYYYMMDD_HHMMSS.tlog"
        """
        cls.logName = logName
        if cls.defaultProps is None:
            propName = cls.propName
            if propName is None:
                propName = os.path.basename(logName)
                propName = os.path.splitext(propName)[0]
            cls.setProps(propName)


    @classmethod
    def setLogToStd(cls, on):
        """ Set logging to stdout
        :on: output to screen
            default: log to screen
        """
        if on is None:
            on = True
        cls.logToScreen = on

    @classmethod
    def setLogStdTs(cls, on=None):
        """ Set stdout log to have timestamp prefix
        """
        if on is None:
            on = True
        cls.stdOutHasTs = on


    @classmethod
    def setupLogging(cls, logName=None,propName=None, dp=None,
                     logToScreen=None,
                     stdOutHasTs=None):
        """
        Setup writing to log file ( via lg(string)) if not already setup
        :logName: name or prefix to log file
        :propName: name for properties file
                default: generated
        :dp: number of decimal places in timestamp
                Iff present, modify current setting
        :logToScreen: put log to screen in addition to log file
            default: output goes to both
            iff present, modify current setting
        :stdOutHasTs: put timestamp on STDOUT (screen)
            default: no timestamp on screen
            if present, modify current setting
        """
            
        if dp is not None:
            cls.decpl = dp          # Set/change default ts decimal places
        if logToScreen is not None:
            cls.logToScreen = logToScreen
        if stdOutHasTs is not None:
            cls.stdOutHasTs = stdOutHasTs
        if propName is not None:
            cls.propName = propName
        if cls.started is True:
            return cls.logWriter
        
        if logName is None:
            logName = cls.logName
    
        if logName is None:
            script_name = os.path.basename(sys.argv[0])
            script_name = os.path.splitext(script_name)[0]
            logName = script_name
        if not os.path.isabs(logName):
            cwd = os.getcwd()
            dir_base = os.path.basename(cwd)
            if dir_base == "src":
                log_dir = os.path.join("..", "log")  # Place in sister directory
                log_dir = os.path.abspath(log_dir)
            else:
                log_dir = "log"
            logName = os.path.join(log_dir, logName)
        if "." not in logName:
            if logName.endswith("_"):
                pass
            else:
                logName += "_"
            ts = cls.getTs()
            logName += ts
            cls.logName = logName
            logName += "."
            logName += cls.logExt  # Default extension
            cls.logName = logName
        cls.logName = logName    

        base_file = os.path.abspath(cls.logName)
        directory = os.path.dirname(base_file)
        if not os.path.exists(directory):
            try:
                os.mkdir(directory)
            except:
                raise TraceError("Can't create logging directory %s"
                                     % directory)
                sys.exit(1)
        
            print("Logging Directory %s  created\n"
                  % os.path.abspath(directory))

        fw = None
        try:
            abs_logName = os.path.abspath(cls.logName)
            fw = open(abs_logName, "w")
            cls.logWriter = fw
        except IOError as e:
            print("Can't open logWriter %s - %s" % (abs_logName, e))
            sys.exit(1)
        cls.started = True
        atexit.register(cls.onexit)        # close down at end
        cls.lg("Creating Log File Name: %s" % abs_logName)
        cls.setProps(cls.propName)         # Setup properties file

        return fw


    @classmethod
    def select_all(cls, level=1):
        """ Trace all known flags at level 1
        """
        for flag in cls.getAllTraceFlags():
            cls.setTraceFlag(flag, level)

    


    @classmethod
    def select_none(cls, level=0):
        """ Trace all known flags at level 0
        """
        for flag in cls.getAllTraceFlags():
            cls.setTraceFlag(flag, level)


    @classmethod
    def lg(cls, msg="", trace_flag=None, level=1, to_stdout=None, dp=None):
        """
        Log string to file, and optionally to console STDOUT display is based on
        trace info
        @param msg
                   - message to output
        @param trace_flag
                   - when to trace - None - always
        @param level
                   - level to trace - default 1
        @param to_stdout
                   - put output to STDOUT (screen) in addition to log file
                     default: use setup value
        @param dp decimal points in timestamp seconds
                default: use pgm default
        @throws IOException
       
        @throws IOException
        """
        if not SlTrace.trace(trace_flag, level):
            return

        try:
            cls.setupLogging()
        except:
            print("IOException in lg setupLogging")
            return

        if dp is None:
            dp = cls.decpl 
        ts = cls.getTs(dp=dp)
        if to_stdout is None:
            to_stdout = cls.logToScreen
        if to_stdout:
            prefix = ""
            if cls.stdOutHasTs:
                prefix += " " + ts
            try:
                print(prefix + " " + msg)
                sys.stdout.flush()   # Force output
            except:
                print("Unexpected error:", sys.exc_info()[0])
            
        if cls.closed:
            return
        
        if cls.logWriter is None:
            print("Can't write to log file")
            return

        try:
            print(" %s %s"  % (ts, msg),
                  file=cls.logWriter)
            cls.logWriter.flush()    # Force output
        except IOError as e:
            print("IOError in lg write %s" % str(e))
        except:
            print("Unexpected error:", sys.exc_info()[0])   


    """
    Append string to log to be logged via next lgln() call
    
    @throws IOException
    """
    @classmethod
    def lgs(cls, msg):
        if cls.lgsString is None:
            lgsString = msg
        else:
            lgsString += msg

    """
    Output staged string to log
    
    @throws IOException
    """
    @classmethod
    def lgln(cls):
        if cls.lgsString is None:
            cls.lgsString = ""

        cls.lg(cls.lgsString)
        cls.lgsString = None # Flush pending

    @classmethod
    def save_propfile(cls):
        """ Save properties file - snapshot
            Can be called repeatedly, also called via atexit
        """
        print("Executing save_propfile")
        if not cls.update:
            print("Not writing updated properties file")
            return
        
        try:
            if cls.defaultProps is not None:
                abs_propName = cls.defaultProps.get_path()
                if cls.newExt is not None:
                    m = re.match(r'(^.*)\.[^.]*$', abs_propName)
                    if m:
                        abs_propName = m[1] + "." + cls.newExt
                tsfmt = "%Y%m%d_%H%M%S"
                ts = datetime.now().strftime(tsfmt)
                title = f" {abs_propName}  {ts}"
                cls.lg(f"Saving properties file {title}")
                cls.propPathSaved = abs_propName
                outf = open(abs_propName, "w")
                cls.defaultProps.store(outf, title)
                cls.defaultProps = None     # Flag as no longer available
                outf.close()
        except IOError as e:
            tbstr = traceback.extract_stack()
            cls.lg("Save propName %s store failed %s - %s"
                    % (abs_propName, tbstr), str(e))
    
    @classmethod
    def onexit(cls):
        cls.save_propfile()
        try:
            if not cls.closed and cls.logWriter is not None:
                abs_logName = os.path.abspath(cls.logName)
                cls.lg("Closing log file %s"
                    % abs_logName)
                cls.logWriter.close()
                cls.closed = True
                cls.logWriter = None        # Flag as not available
        except IOError as e:
            cls.closed = True
            tbstr = traceback.extract_stack()
            cls.lg("Close logfile %s failed %s - %s"
                    % (abs_logName, tbstr), str(e))
        cls.closed = True
        cls.runningJob = False

    @classmethod
    def getTs(cls, dp=0):
        """
        Get / generate time stamp Format: YYYYMMDD_HHMMSS
        :dp: seconds decimal places default: 0
        """
        tsfmt = "%Y%m%d_%H%M%S"
        if dp > 0:
            tsfmt = "%Y%m%d_%H%M%S_%f"
        ts = datetime.now().strftime(tsfmt)
        if dp > 0:
            if dp >= 6:
                pass        # Whole string
            else:
                ts = ts[:dp-6]      # remove portion of _[dddddd]
        return ts

    @classmethod
    def ts_to_datetime(cls, ts):
        """ Convert time stamp to datetime object
        :ts: time stamp "%Y%m%d_%H%M%S" or "%Y%m%d_%H%M%S_%f"
        :returns: datetime object
        """
        tsfmt = "%Y%m%d_%H%M%S"
        base_len = 15           # No "_dddddd"
        if len(ts) > base_len:
            ddig = base_len - len(ts) -1        # omit "_" separator
            tsfmt += "_%f"          # Get decimal fraction
            ts += ddig * "0"        # get 6 digits of uSec
        dtobj = datetime.strptime(ts, tsfmt)
        return dtobj
    
    @classmethod
    def ts_diff(cls, ts1=None, ts2=None):
        """ Time, in seconds, between first time (ts1) and second time
        :ts1: first time stamp
        :ts2: second time stamp
        :returns: difference in seconds (float)
        """
        t1 = cls.ts_to_datetime(ts1)    
        t2 = cls.ts_to_datetime(ts2)
        diff = (t2-t1).total_seconds()
        return diff


    @classmethod
    def setProps(cls, propName=None, newExt=None, update=None):
        """
        Set up based on Java style properties file
        :propName: given properties file name
            default: generated from script
        :newExt: Extension of created properties file
            default: Created properties file is same as source propertites
        :update: write out updated properties file a end (save_propfile)
        @throws IOException
        """
        if propName is not None:
            cls.propName = propName
        cls.newExt = newExt
        if update is not None:
            cls.update = update
        
        if cls.propName is None:
            script_name = os.path.basename(sys.argv[0])
            script_name = os.path.splitext(script_name)[0]
            cls.propName = script_name
            
        if os.path.splitext(cls.propName)[1] == "":
            cls.propName += ".properties"
            
        if not os.path.isabs(cls.propName):
            cwd = os.getcwd()
            dir_base = os.path.basename(cwd)
            if dir_base == "src":
                prop_dir = os.path.dirname(cwd)
                cls.propName = os.path.join(prop_dir, cls.propName)
            else:
                cls.propName = os.path.abspath(cls.propName)
            
        cls.defaultProps = JavaProperties(cls.propName)

        cls.loadTraceFlags()        # Populate flags from properties
                                     


    @classmethod
    def getLogPath(cls):
        """ Returns absolute log file path name
        """
        return os.path.abspath(cls.logName)


    @classmethod
    def getPropKeys(cls, startswith=None):
        """
        get properties keys
        :startswith: starting with this string
                default: All keys
        """
        props = cls.defaultProps.getPropKeys(startswith=startswith)
        return props

    @classmethod
    def getMemory(cls):
        """ Get current memory usage for this process
        """
        import importlib
        try:
            psutil = importlib.import_module("psutil")
        except:
            cls.lg("getMemory - needs pip install of psutil")
            sys.exit(1)
            
        process = psutil.Process(os.getpid())
        mem = process.memory_info().rss  # in bytes
        cls.mem_used_change = mem - cls.mem_used
        cls.mem_used = mem
        return cls.mem_used 

    @classmethod
    def getMemoryChange(cls):
        """ Get current memory usage change since last
        getMemory call NOTE: no check on memory done here
        """
        return cls.mem_used_change


    @classmethod
    def getPropPath(cls):
        """ Returns absolute Properties file path name
        """
        abs_propName = cls.defaultProps.get_path()
        return abs_propName


    @classmethod
    def getPropPathSaved(cls):
        return cls.propPathSaved
    
    
    @classmethod
    def getLevel(cls, trace_name):
        trace_name = trace_name.lower()
        cls.recordTraceFlag(trace_name)
        if trace_name not in cls.traceFlags:
            v = 0
            cls.traceFlags[trace_name] = v
        v = cls.traceFlags[trace_name]
        if v is None or v == '':
            v = 0            # Not there == 0
        if isinstance(v, str):
            v = str.lower()
            if v == "true":
                v = True
            elif v == "false":
                v = False
            else:
                v = int(v)
        return v



    @classmethod
    def setLevel(cls, trace_name, level=1):
        trace_name = trace_name.lower()
        cls.recordTraceFlag(trace_name, level=level)
        flag_key = cls.getTraceFlagKey(trace_name)
        cls.setProperty(flag_key, level)
        if isinstance(level, str):
            level = level.lower()
            if level == "true":
                level = True
            elif level == "false":
                level = False
            else:
                level = int(level)
        if trace_name == "all":
            cls.traceAll = level
        else:
            cls.traceFlags[trace_name] = level


    @classmethod
    def traceVerbose(cls, level=1):
        return cls.trace("verbose", level=level)


    @classmethod
    def getTraceFlags(cls):
        """
        return array of set trace flags
        """
        return cls.traceFlags.keys()

    
    
    """
    Record flag for saving
    Note value may change
    """
    @classmethod
    def recordTraceFlag(cls, flag, level=1):
    ###    if flag in cls.recTraceFlags:
    ###       return                # Already here - don't
        
        cls.recTraceFlags[flag] =  level
        flag_key = cls.getTraceFlagKey(flag)
        cls.setProperty(flag_key, level, onlyifnew=True)


    @classmethod
    def getTraceValueFromProp(cls, name):
        """
        Return flag value, -1 if none
        """
        flagstr = cls.getProperty(cls.getTraceFlagKey(name))
        if flagstr == "":
            return -1

        return int(flagstr)


    @classmethod
    def loadTraceFlags(cls):
        """
        load trace flags from properties
        """
        propfile = cls.defaultProps.get_path()
        SlTrace.lg(f"Trace levels from properties file {propfile}")
        props = cls.defaultProps.get_properties()
        pattern = r"^\s*" + cls.traceFlagPrefix + r"\.(.*)"
        r = re.compile(pattern)
        ### TBD I need to think about what is going on here
        keys =  list(props.keys())
        for key in keys:
            m = r.match(key)
            if m:
                post_prefix = m[1]
                name = post_prefix        # stuff after prefix
                value = props[key]  # Default to property value
                mn = re.match(r'(\w+)\s*=\s*(\S.*)', post_prefix)
                if mn:
                    name = mn[1]
                    value = mn[2]
                    break
                cls.setLevel(name, value)
        all_flags = cls.getAllTraceFlags()
        all_flags_str = ",".join(all_flags)
        cls.lg("loadTraceFlags: %s" % all_flags_str)
        for flag in all_flags:
            level = cls.getLevel(flag)
            cls.lg(f"{flag} = {level}")

    
    @classmethod
    def getAllTraceFlags(cls):
        return cls.recTraceFlags.keys()
    
    
    @classmethod
    def getTraceFlagKey(cls, name):
        key = cls.traceFlagPrefix + "." + name
        return key


    @classmethod
    def setDebug(cls, level=1):
        """
        @param debug
                   to set
        """
        cls.setLevel("debug", level)


    @classmethod
    def setVerbose(cls, level=1):
        """
        @param level
        """
        cls.setLevel("verbose", level)


    @classmethod
    def getVerbose(cls):
        """
        @return the verbose
        """
        return cls.getLevel("verbose")


    """
    Trace if at or above this level
    """
    @classmethod
    def trace(cls, flag=None, level=None):
        if flag is None:
            return True
        
        if level is None:
            level = 1
        if level < 1:
            return False # Don't even look

        return cls.traceLevel(flag) >= level


    """
    Return trace level
    """
    @classmethod
    def traceLevel(cls, flag):
        traceLevel = cls.getLevel(flag)
        return traceLevel


    @classmethod
    def deleteProperty(cls, key):
        """ Delete property from properties file
        """
        if cls.defaultProps is None:
            cls.setupLogging()
            cls.setProps()
        if cls.hasProp(key):
            cls.defaultProps.deleteProperty(key)


    @classmethod
    def getProperty(cls, key, default=""):
        """    
        :key:property key
        :default: return if Not found default: ""
        ###@return property value, "" if none
        """
        if cls.defaultProps is None:
            cls.setupLogging()
            cls.setProps()
        return cls.defaultProps.getProperty(key, default)


    @classmethod
    def setProperty(cls, key, value, onlyifnew=False):
        if cls.defaultProps is None:
            cls.setupLogging()
            cls.setProps()
        if not cls.hasProp(key) or not onlyifnew:
            cls.defaultProps.setProperty(key, value)

    @classmethod
    def getLogFile(cls):
        """ Returns output file to support situations
        which can't be logged directly via lg
        Note that no time stamps will be shown
        """
        return cls.setupLogging()

    @classmethod
    def getSourceDirs(cls, string=False):
        """ Returns list of source directories
        """
        dirs = cls.getAsStringArray("source_files")
        dirpaths = []
        for dir in dirs:
            dirpaths.append(os.path.abspath(dir)) 
        if string:
            return " ".join(dirpaths)
        
        return dirpaths
    
    @classmethod
    def getSourcePath(cls, fileName, req=True, report=True):
        """
        Get source absolute path Get absolute if fileName is not absolute TBD handle
        chain of paths like C include paths
        
        :fileName:
        :req: Required default: Must be found or error or raise TraceError
        :report: Report if can't find default: report to log,stderr if can't find
        :return: absolute file path if found, else None
        """
        if not os.path.isabs(fileName):
            dirs = cls.getAsStringArray("source_files")
            searched = []
            for pdir in dirs:
                inf = os.path.join(pdir, fileName)
                inf = os.path.abspath(inf)
                if os.path.exists(inf):
                    try:
                        return os.path.realpath(inf)
                    except IOError as e:
                        raise TraceError("Problem with path %s" % (inf))

                searched.append(os.path.realpath(inf))
            if report:
                cls.lg("%s was not found" % fileName)
                if len(dirs) > 0:
                    cls.lg("Searched in:")
                    for dirp in dirs:
                        dirpath = os.path.abspath(dirp)
                        cls.lg("\t%s" % dirpath)
            if req:
                raise TraceError("Can't find file %s in %s" % (fileName, dirs))
            
            return None
        # Return unchanged
        if not os.path.exists(fileName):
            if report:
                cls.lg("Can't find file %s" % (fileName))
            if req:    
                raise TraceError("Can't find file %s" % (fileName))
            
            return None
            
        return fileName # Already absolute path

    @classmethod
    def getIncludePath(cls, fileName):
        """
        Get include absolute path Get absolute if fileName is not absolute TBD handle
        chain of paths like C include paths
        
        @param fileName
        @return absolute file path, "" if not found
        """
        if not os.path.isabs(fileName):
            dirs = cls.getAsStringArray("include_files")
            searched = []
            for dirp in dirs:
                inf = os.path.join(dir, fileName)
                if os.path.exists(inf) and not os.path.isdir(inf):
                    try:
                        return os.path.realpath(inf)
                    except IOError as e:
                        print("Problem with path %s,%s" % (dirp, fileName), file=sys.stderr)
      
            print("%s was not found\n" % fileName, file=sys.stderr)
            if len(dirs) > 0:
                print("Searched in:\n")
                for dirp in dirs:
                    dirpath = os.path.realpath(dirp)
                    print("\t%s\n" % dirpath)
            return "" # Indicate as not found

        return fileName # Already absolute path


    @classmethod
    def getAsStringArray(cls, propKey):
        """
        Get default properties key with value stored as comma-separated values as an
        array of those values If propKey not found, return an empty array
        
        @param propKey
        @return array of string values
        """
        valstr = cls.getProperty(propKey)
        vals = valstr.split(',')
        return vals


    @classmethod
    def setTraceFlag(cls, trace_name, level=1):
        """
        Fast, lowlevel trace level setting
        Used for interactive trace changes
        @param trace_name
        @param level
        """
        cls.traceFlags[trace_name] = level

    @classmethod
    def hasProp(cls, key):
        """ Check if property is already present
        :key: property key
        :returns: True iff property is present
        """
        return cls.defaultProps.hasProp(key)
            
    
if __name__ == "__main__":
    import argparse
    propfile = "none_expected"
    propfile_new_ext = "prop_out"
    propfile_update = True
    show_passes = True
    ###show_passes = False
    quit_on_fail = True      # True - stop testing on first failure
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--propfile', default=propfile,
                        help=("properties file name"
                              " (default:generate from script name)"))
    parser.add_argument('-n', '--propfile_new_ext', default=propfile_new_ext,
                        help=("new properties file ext"
                              " (default:no extension change)"))
    parser.add_argument('-u', '--propfile_update', default=propfile_update,
                        help=("update properties file"
                              " (default:write out new properties file)"))
    parser.add_argument('-s', '--show_passes', action='store_true', default=show_passes,
                        help=(f"Show passes"
                              f" (default: {show_passes}"))
    parser.add_argument('-q', '--quit_on_fail', action='store_true', default=quit_on_fail,
                        help=(f"Quit on first failure"
                              f" (default: {quit_on_fail}"))

    args = parser.parse_args()             # or die "Illegal options"
    
    propfile = args.propfile
    propfile_new_ext = args.propfile_new_ext
    propfile_update = args.propfile_update
    show_passes = args.show_passes
    quit_on_fail = args.quit_on_fail
        
    def test_fail(msg):
        """ Show error and quit if quit_on_first_error
        """
        SlTrace.lg("FAIL: %s" % msg)
        if quit_on_fail:
            SlTrace.lg("Quitting on first fail")
            sys.exit(1)

            
    def test_pass(msg):
        """ Show pass if show_passes
        """
        print_msg = "Pass: %s" % msg
        if show_passes:
            print(print_msg)
        SlTrace.lg(print_msg, to_stdout=False)
            
    logName = "sltest"
    SlTrace.setupLogging(logName, propName=propfile)     # Setup log/properties names
    SlTrace.setProps(newExt=propfile_new_ext, update=propfile_update)
    SlTrace.lg("args: {}\n".format(args))
    SlTrace.lg("setupTest()")
    flag = "sf1"
    SlTrace.setLevel(flag)
    level_got = SlTrace.getLevel(flag)
    if level_got != 1:
        print("level_got: %d != 1" % level_got)
        sys.exit(1)
    flag = "sf2"
    level = 3
    SlTrace.setLevel(flag, level)
    level_got = SlTrace.getLevel(flag)
    if level_got != level:
        test_fail("level_got: %d != %d" % (level_got, level))

    
    if SlTrace.trace(flag, level):
        test_pass("traced %s(%s) with trace(%d)" % (flag, level_got, level))
    else:
        test_fail("FAILED trace %s(%s) with trace(%d)" % (flag, level_got, level))
    
    if SlTrace.trace(flag, level_got-1):
        test_pass("Correctly traced %s(%s) with trace(%d)" % (flag, level_got, level_got-1))
    else:
        test_fail("ERRONEOUSLY skipped trace %s(%s) with trace(%d)" % (flag, level_got, level_got-1))
    
    if SlTrace.trace(flag, level_got+1):
        test_fail("ERRONEOUSLY traced %s(%s) with trace(%d)" % (flag, level_got, level_got+1))
    else:
        test_pass("Correctly skipped trace %s(%s) with trace(%d)" % (flag, level_got, level_got+1))
        
    SlTrace.setFlags("f1=1,f2=2,f3=3,fnone")
    tdict = {"f1" : 1, "f2" : 2, "f3" : 3, "fnone" : None}
    for flag, level in tdict.items():
        if level is None:
            level = 1           # Default setting
        trace_level = level
        if SlTrace.trace(flag, trace_level):
            if trace_level is None:
                test_pass("flag %s(%d) traced(None)" % (flag, level))
            else:
                test_pass("flag %s(%d) traced(%d)" % (flag, level, trace_level))
                
        else:
            if trace_level is None:
                test_fail("flag %s(%d) skipped(None)" % (flag, level))
            else:
                test_fail("flag %s(%d) skipped(%d)" % (flag, level, trace_level))
    SlTrace.lg("Making the following output only to log")
    SlTrace.setupLogging(logToScreen=False, dp=6)
    for i in range(250):
        SlTrace.lg(f"{i}: only to log file")
    SlTrace.setupLogging(logToScreen=True, dp=0)
    SlTrace.lg("Output is now to both log file and screen")
    SlTrace.setupLogging(stdOutHasTs=True)
    SlTrace.lg("Timestamp now included on screen")
    SlTrace.setupLogging(dp=4)
    SlTrace.lg("with new timestamp precision")
    SlTrace.lg("More of the same")
    SlTrace.setupLogging(dp=0)
    SlTrace.lg("dp back at 0")
    SlTrace.setLogStdTs(False)
    SlTrace.lg("No timestamp to STDOUT")
    test_memory = False
    test_memory = True
    if test_memory:
        mem = SlTrace.getMemory()
        SlTrace.lg(f"memory = {mem} bytes")
    SlTrace.lg("End of Test")
