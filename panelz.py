import numpy as np
import graphics as g
from fractions import Fraction

from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color

class Panel:
    pass


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def copy(self):
        return Point(self.x, self.y)

    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ")"


class Rectangle:
    def __init__(self, tl=Point(0, 0), br=Point(1, 1)):
        self.tl = tl
        self.br = br
        self.children = []
        self.hasRows = False
        self.hasCols = False

    def width(self):
        return abs(self.br.x - self.tl.x)

    def height(self):
        return abs(self.br.y - self.tl.y)

    def hsplit(self, num=2, ratios=[]):
        if(self.children == []):
            self.hasRows = True
            if len(ratios) < num:
                ratios = [Fraction(1, num) for i in range(len(ratios), num)]
            start = self.tl.copy()
            for i in range(num):
                # cannot use self.width and height functions as
                # they return absolutes, we need sign as well here
                h = (self.br.y - self.tl.y) * ratios[i]
                self.children.append(
                    Rectangle(start, Point(self.br.x, start.y + h)))
                start = Point(start.x, start.y + h)
        else:
            print(
                "This rectangle already has been split before. To change split, unsplit and split again.")
        return self.children

    def vsplit(self, num=2, ratios=[]):
        if(self.children == []):
            self.hasCols = True
            if len(ratios) < num:
                ratios = [Fraction(1, num) for i in range(len(ratios), num)]
            start = self.tl.copy()
            for i in range(num):
                # cannot use self.width and height functions as
                # they return absolutes, we need sign as well here
                w = (self.br.x - self.tl.x) * ratios[i]
                self.children.append(
                    Rectangle(start, Point(start.x + w, self.br.y)))
                start = Point(start.x + w, start.y)
        else:
            print(
                "This rectangle already has been split before. To change split, unsplit and split again.")

        return self.children

    def numRows(self):
        if self.hasRows:
            return len(self.children)
        else:
            return 1

    def numCols(self):
        if self.hasCols:
            return len(self.children)
        else:
            return 1

    def unsplit(self):
        self.children = []
        self.hasRows = False
        self.hasCols = False
        return self.children

    def __str__(self):
        return "[ " + str(self.tl) + ", " + str(self.br) + " ]"


class PanelDisplay:
    def __init__(self, displayType, width, height):
        super().__init__()
        self.displayType = displayType
        self.width = width
        self.height = height

    def drawRectangle(self, r, outline_colour="black", outline_width=1, fill=None):
        pass

    def show(self):
        pass


class GraphicsPanelDisplay(PanelDisplay):
    def __init__(self, width=600, height=400):
        super().__init__("Graphics Panel Display", width, height)
        self.win = g.GraphWin("Rectangles", self.width, self.height)

    def drawRectangle(self, r, outline_colour="black", outline_width=1, fill=None):
        gr = self.gRectangle(r)
        gr.setOutline(outline_colour)
        gr.setWidth(outline_width)
        gr.draw(self.win)

    def show(self):
        self.win.getMouse()  # pause for click in window
        self.win.close()

    @classmethod
    def gPoint(cls, p):
        return g.Point(p.x, p.y)

    @classmethod
    def gRectangle(cls, r):
        return g.Rectangle(cls.gPoint(r.tl), cls.gPoint(r.br))

class WandPanelDisplay(PanelDisplay):
    def __init__(self, width=600, height=400):
        super().__init__("Graphics Panel Display", width, height)
        self.draw = Drawing()

    def drawRectangle(self, r, outline_colour="black", outline_width=1, fill=None):
        self.draw.stroke_color = Color(outline_colour)
        self.draw.stroke_width = outline_width
        self.draw.rectangle(left=r.tl.x, top=r.tl.y, right=r.br.x, bottom=r.br.y)

    def show(self):
        with Image(width=self.width,
                height=self.height,
                background=Color('lightblue')) as img:
            self.draw.draw(img)
            img.save(filename='draw-panel.gif')

    @classmethod
    def gPoint(cls, p):
        return g.Point(p.x, p.y)

    @classmethod
    def gRectangle(cls, r):
        return g.Rectangle(cls.gPoint(r.tl), cls.gPoint(r.br))



OUTLINE_COLOURS = ["red", "blue", "magenta", "green"]


def Draw(panelDisplay, r, depth=0, scalex=None, scaley=None, offset_pct = Fraction(5, 100)):
    if scalex == None:
        scalex = panelDisplay.width/r.width()
        scaley = panelDisplay.height/r.height()
    offsetx = scalex * offset_pct
    offsety = scaley * offset_pct
    drawr = Rectangle(Point(r.tl.x * scalex, r.tl.y * scaley),
                  Point(r.br.x * scalex, r.br.y * scaley))
    panelDisplay.drawRectangle(drawr, outline_colour=OUTLINE_COLOURS[depth], outline_width=(
        5-depth)*2)
    if r.hasCols or r.hasRows:
        for rc in r.children:
            Draw(panelDisplay, rc, depth=(depth+1), scalex=scalex, scaley=scaley)


if __name__ == "__main__":
    panelDisplay = WandPanelDisplay()
    r = Rectangle()
    r.vsplit()
    for rc in r.children:
        rc.vsplit()
        for rcc in rc.children:
            rcc.hsplit()
    Draw(panelDisplay, r)
    panelDisplay.show()
