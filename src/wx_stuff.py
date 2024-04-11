#wx_stuff.py    04Apr2024
""" support functions
"""
import wx

def wx_Point(x, y=None):
    """ Force int args
    :x: x value or wx.Point if y is None
    :y: y value
    :returns: wx.Point
    """
    if y is None:
        return x
    
    return wx.Point(int(x), int(y))
