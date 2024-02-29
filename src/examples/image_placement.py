# image_placement.py 21Feb2024 crs from: wxPython-In-Action/Chapter-12/draw_image.py
# This one shows how to draw images on a DC.
import os
import wx
import random
random.seed()

class RandomImagePlacementWindow(wx.Window):
    def __init__(self, parent, image):
        wx.Window.__init__(self, parent)
        self.photo = image.ConvertToBitmap()

        # choose some random positions to draw the image at:
        self.positions = [(10,10)]
        for x in range(50):
            x = random.randint(0, 1000)
            y = random.randint(0, 1000)
            self.positions.append( (x,y) )
            
        # Bind the Paint event
        self.Bind(wx.EVT_PAINT, self.OnPaint)


    def OnPaint(self, evt):
        # create and clear the DC
        dc = wx.PaintDC(self)
        brush = wx.Brush("sky blue")
        dc.SetBackground(brush)
        dc.Clear()

        # draw the image in random locations
        for x,y in self.positions:
            dc.DrawBitmap(self.photo, x, y, True)

        
class TestFrame(wx.Frame):
    def __init__(self):
        src_dir = os.path.dirname(__file__)
        os.chdir(src_dir)
        wx.Frame.__init__(self, None, title="Loading Images",
                          size=(640,480))
        img = wx.Image("masked-portrait.png")
        win = RandomImagePlacementWindow(self, img)
        

#app = wx.PySimpleApp()
app = wx.App()
frm = TestFrame()
frm.Show()
app.MainLoop()