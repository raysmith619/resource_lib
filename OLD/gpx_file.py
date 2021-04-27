# gpx_file.py    09May2020    crs
""" GPX file loading 
"""
import os
import re
from tkinter import filedialog
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, Comment
import datetime
from xml.etree import ElementTree
from xml.dom import minidom

from select_trace import SlTrace
from select_error import SelectError

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

class GPXPoint:
    def __init__(self, lat=None, long=None):
        self.lat = lat
        self.long = long
        
    def __str__(self):
        return f"GPXPoint: lat:{self.lat} Long:{self.long}"

    def latLong(self):
        return self.lat, self.long
        
class GPXTrackSegment:
    def __init__(self):
        self.points = []
        
    def __str__(self):
        npts = len(self.points)
        t_str = f"GPXTrackSegment: ({npts} points"
        if npts > 0:
            t_str += f" starting with {self.points[0]}"
        return t_str
    
    def add_points(self, *points):
        """ Add point(s) to segment
        :points: zero or more args, each of which is a point or list of points
         (GPXPoint) to add
        """
        for pts in points: 
            if not isinstance(pts, list):
                pts = [pts]         # Make list of one
            self.points.extend(pts)
            
    def get_points(self):
        return self.points
       
        
class GPXFile:
    """ simple point loading 
    """
    def __init__(self, file_name=None):
        self.ns = {"xsi" : "http://www.w3.org/2001/XMLSchema-instance",
               "ogr" : "http://osgeo.org/gdal",
               "" : "http://www.topografix.com/GPX/1/1",
               }
        self.bns = "{" + self.ns[""] + "}"        # Shorter name space,
        
        self.file_name = file_name
        self.track_segments = []
        if file_name is not None:
            gpx = self.load_file(file_name)
            if gpx is None:
                raise SelectError(f"load GPXFile {file_name} failed")

                        # since namespace={} doesn't appear to work

            
    def add_segments(self, *segments):
        """ Add  to file
        :segments: zero or more args, each of which is a segment or list of segments
         (GPSTrackSegment)
        """
        for segs in segments:
            if not isinstance(segs, list):
                segs = [segs]       # Make list of one
            self.track_segments.extend(segs)
    
    def load_file(self, file_name):
        """ load .GPX file (actually a XML file)
        :file_name: file name
        :returns: self if successful, else None
        """
        if file_name is None:
            file_name = filedialog.askopenfilename(
            initialdir= "../data/trail_system_files",
            title = "Open trail File",
            filetypes= (("trail files", "*.gpx"),
                        ("all files", "*.*"))
                       )
            if file_name is not None:
                SlTrace.report(f"No file selected")
                return None
        
        if not os.path.isabs(file_name):
            file_name = os.path.join("..", "data", "trail_system_files", file_name)
            if not os.path.isabs(file_name):
                file_name = os.path.abspath(file_name)
                if re.match(r'.*\.[^.]+$', file_name) is None:
                    file_name += ".gpx"         # Add default extension
        if not os.path.exists(file_name):
            SlTrace.report(f"File {file_name} not found")
            return None

        self.file_name = file_name
        SlTrace.lg(f"Parsing file: {file_name}", "gpx_trace")
        """
        TBD - build name space from root attributes
        """
        SlTrace.lg(f"bns: base namespace name:{self.bns}", "gpx_trace")
        
        self.track_segments = []           # Initialize / re-initialize
        tree = ET.parse(file_name)
        root = tree.getroot()
        SlTrace.lg(f"root:{root} root.tag:{root.tag}", "gpx_trace")
        SlTrace.lg(f"root.attrib: {root.attrib}", "gpx_trace")
        ns = self.ns
        bns = self.bns        # Shorter name space,
                            # since namespace={} doesn't appear to work
        trks = root.findall(f"{bns}trk")
        for trk in trks:
            SlTrace.lg(f"trk: {trk}", "gpx_trace")
            trksegs = trk.findall(f"{bns}trkseg", ns) # DOESN'T WORK
            for trkseg in trksegs:
                SlTrace.lg(f"    trkseg: {trkseg}", "gpx_trace")
                tseg = GPXTrackSegment()
                self.add_segments(tseg)
                trkpts = trkseg.findall(f"{bns}trkpt")
                if SlTrace.trace("gpx_trace"):
                    npts = len(trkpts)
                    SlTrace.lg(f"{npts} points", "gpx_trace")
                    if npts > 0:
                        trkpt = trkpts[0]
                        SlTrace.lg(f"        lat: {trkpt.attrib['lat']}"
                                   f" lon: {trkpt.attrib['lon']}", "gpx_trace")
                points = []    
                for trkpt in trkpts:
                    SlTrace.lg(f"        lat: {trkpt.attrib['lat']}"
                               f" lon: {trkpt.attrib['lon']}", "gpx_trace_pts")
                    pt = GPXPoint(lat=float(trkpt.attrib['lat']),
                                  long=float(trkpt.attrib['lon']))
                    points.append(pt)
                tseg.add_points(points)
        return self        

    def get_segments(self):
        """  Get track segments
        :returns: list of GPXTrackSegment
        """
        return self.track_segments

    def set_segments(self, segments):
        self.track_segments = []
        self.add_segments(segments)
            
    def get_points(self):
        """ Return list of points
        """
        points = []
        for seg in self.get_segments():
            points.extend(seg.get_points())
        return points

    def save_file(self, file_name):
        out_file = file_name
        if file_name is None:
            out_file = "new_gpx_" + SlTrace.getTs()
        if not os.path.isabs(out_file):
            out_file = os.path.basename(out_file)
            out_file = os.path.join("..", "new_data", out_file)
        pm = re.match(r'^.*\.[^.]+$', out_file)
        if pm is None:
            out_file += ".gpx"
        out_file = os.path.abspath(out_file)
        SlTrace.lg(f"Output file: {out_file}")
        gpx_attr = {'version'               : "1.1",
                    'creator'               : "GDAL 3.0.4",
                    'xmlns:xsi'             : "http://www.w3.org/2001/XMLSchema-instance",
                    'xmlns:ogr'             : "http://osgeo.org/gdal",
                     'xmlns'                : "http://www.topografix.com/GPX/1/1",
                     'xsi:schemaLocation'   : "http://www.topografix.com/GPX/1/1",
                     }
        gpx_top = Element('gpx', gpx_attr)
        generated_on = str(datetime.datetime.now())
        comment = Comment(f"Created {generated_on} via surveyor.py by crs")
        gpx_top.append(comment)
        comment = Comment(f"Source code: GitHub raysmith619/PlantInvasion")
        gpx_top.append(comment)
        n_seg = 0
        n_pt = 0
        for track_segment in self.get_segments():
            trk = SubElement(gpx_top, 'trk')
            ###gpx_top.append(trk)
            trkseg = SubElement(trk, 'trkseg')      # We only have one trkseg per trk
            ###trk.append(trkseg)
            n_seg += 1
            for seg_point in track_segment.get_points():
                trkpt = SubElement(trkseg, 'trkpt',
                                   {'lat' : str(seg_point.lat),
                                   'lon' : str(seg_point.long),
                                   })
                ###trkseg.append(trkpt)
                n_pt += 1
        SlTrace.lg(f"GPX File: {n_seg} segments {n_pt} points")
        pretty_str = prettify(gpx_top)
        
        if SlTrace.trace("gpx_output"):
            SlTrace.lg(pretty_str)
        if SlTrace.trace("gpx_rough_outupt"):
            rough_string = ElementTree.tostring(gpx_top, 'utf-8')
            SlTrace.lg(f"rough_string:{rough_string}")
        try:
            fout = open(out_file, "w")
            fout.write(pretty_str)
            fout.close()
        except IOError as e:
            err_msg = f"Error {repr(e)} in creating GPXFile {out_file}"
            SlTrace.lg(err_msg)
            SlTrace.report(err_msg)
            
if __name__ == "__main__":
    ###from tkinter import filedialog
    SlTrace.clearFlags()
    gpx_file = None
    ###gpx_file = r"../data/trail_system_files/merged_tracks.gpx"
    ###gpx_file = r"../data/trail_system_files/track_GPS1.gpx"
    gpx_file = str("C:/Users/raysm/workspace/python/PlantInvasion/data/trail_system_files"
                   "/trails_from_averaged_waypoints_CORRECTED_9nov2018.gpx")
    if gpx_file is None:
        gpx_file = filedialog.askopenfilename(
            initialdir= "../data/trail_system_files",
            title = "Open GPX File",
            filetypes= (("GPX files", "*.gpx"),
                        ("all files", "*.*"))
                       )
    if gpx_file is None or gpx_file == "":
        raise SelectError("No file")
    SlTrace.lg(f"Input: {gpx_file}")
    gpx = GPXFile(gpx_file)
    pts = gpx.get_points()
    segs = gpx.get_segments()
    nseg = len(segs)
    SlTrace.lg(f"{nseg} track segments {len(pts)} Points", "gpx_trace")
    for i, tseg in enumerate(segs):
        SlTrace.lg(f"Segment {i+1}: {tseg}", "gpx_trace")
    
    new_file = os.path.basename(gpx.file_name)
    gpx.save_file(new_file)                