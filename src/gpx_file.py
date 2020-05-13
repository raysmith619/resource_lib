# gpx_file.py    09May2020    crs
""" GPX file loading 
"""
from xml.etree import ElementTree as ET
from select_trace import SlTrace
from select_error import SelectError

class GPXPoint:
    def __init__(self, lat=None, long=None):
        self.lat = lat
        self.long = long
        
    def __str__(self):
        return f"GPXPoint: lat:{self.lat} Long:{self.long}"
       
    def latLong(self):
        return self.lat, self.long
        
class GPXFile:
    """ simple point loading 
    """
    def __init__(self, file_name=None):
        self.file_name = file_name
        self.lon_lat_pts = []
        if file_name is not None:
            self.load_file(file_name)
    
    def load_file(self, file_name):
        """ load .GPX file (actually a XML file)
        :file_name: file name
        """
        """ TBD - build this from root attributes
        """
        SlTrace.lg(f"Parsing file: {file_name}", "gpx_trace")
        ns = {"xsi" : "http://www.w3.org/2001/XMLSchema-instance",
               "ogr" : "http://osgeo.org/gdal",
               "" : "http://www.topografix.com/GPX/1/1",
               }
        bns = "{" + ns[""] + "}"        # Shorter name space,
                        # since namespace={} doesn't appear to work
        SlTrace.lg(f"bns: base namespace name:{bns}", "gpx_trace")
        
        self.lon_lat_pts = []           # Initialize / re-initialize
        tree = ET.parse(file_name)
        root = tree.getroot()
        SlTrace.lg(f"root:{root} root.tag:{root.tag}", "gpx_trace")
        SlTrace.lg(f"root.attrib: {root.attrib}", "gpx_trace")
        bns = "{" + ns[""] + "}"        # Shorter name space,
                            # since namespace={} doesn't appear to work
        trks = root.findall(f"{bns}trk")
        for trk in trks:
            SlTrace.lg(f"trk: {trk}")
            trksegs = trk.findall(f"{bns}trkseg", ns) # DOESN'T WORK
            for trkseg in trksegs:
                SlTrace.lg(f"    trkseg: {trkseg}")
                trkpts = trkseg.findall(f"{bns}trkpt")
                if SlTrace.trace("gpx_trace"):
                    npts = len(trkpts)
                    SlTrace.lg(f"{npts} points")
                    if npts > 0:
                        trkpt = trkpts[0]
                        SlTrace.lg(f"        lat: {trkpt.attrib['lat']}"
                                   f" lon: {trkpt.attrib['lon']}", "gpx_trace")
                    
                for trkpt in trkpts:
                    SlTrace.lg(f"        lat: {trkpt.attrib['lat']}"
                               f" lon: {trkpt.attrib['lon']}", "gpx_trace_pts")
                    pt = GPXPoint(lat=float(trkpt.attrib['lat']),
                                  long=float(trkpt.attrib['lon']))
                    self.lon_lat_pts.append(pt)
        return self.lon_lat_pts        
        
    def get_points(self):
        """ Return list of points
        """
        return self.lon_lat_pts
    
if __name__ == "__main__":
    from tkinter import filedialog
    SlTrace.clearFlags()
    gpx_file = None
    ###gpx_file = r"../data/trail_system_files/merged_tracks.gpx"
    ###gpx_file = r"../data/trail_system_files/track_GPS1.gpx"
    if gpx_file is None:
        gpx_file = filedialog.askopenfilename(
            initialdir= "../../data/trail_system_files",
            title = "Open GPX File",
            filetypes= (("GPX files", "*.gpx"),
                        ("all files", "*.*"))
                       )
    if gpx_file is None or gpx_file == "":
        raise SelectError("No file")
    
    gpx = GPXFile(gpx_file)
    pts = gpx.get_points()
    SlTrace.lg(f"{len(pts)} Points")
    for pt in pts:
        SlTrace.lg(f"lat: {pt.lat} lon: {pt.long}")
                    