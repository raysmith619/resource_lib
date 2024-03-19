#floatcanvas_1.py   06Mar2024  crs from wx.lib.FloatCanvas
import wx 
from wx.lib.floatcanvas import FloatCanvas as fc

class MyFloatCanvas(fc.FloatCanvas):
    def __init__(self):
        super().__init__(None,
                        size=(500, 500),
                        ProjectionFun=None,
                        Debug=0,
                        BackgroundColor="White",
                        )
app = wx.App()
flc = MyFloatCanvas()
# add a circle
cir = flc.Circle((10, 10), 100)
flc.Canvas.AddObject(cir)

# add a rectangle
rect = flc.Rectangle((110, 10), (100, 100), FillColor='Red')
flc.Canvas.AddObject(rect)

flc.Canvas.Draw()