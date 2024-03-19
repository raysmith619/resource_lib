#wx_canvas_panel_parts.py
#Sections:
        upd = wx.RegionIterator(self.grid_panel.GetUpdateRegion())

        if not upd.HaveRects():
            self.draw_items()
        SlTrace.lg(f"Got Rects")    
        while upd.HaveRects():
            rect = upd.GetRect()
            SlTrace.lg(f"Got Rect:{rect}")
            # Repaint this rectangle
            self.draw_items(rect=rect)
            self.draw_items( types=["create_line", "create_cursor"], rect=rect)
            upd.Next()
