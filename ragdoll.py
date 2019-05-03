import numpy as np

from tkinter import Tk, Label, Button, Canvas, Frame, BOTH


STANDART_KPS = np.array(
     [[140.26817181,  46.54231771],
      [133.239308,    62.68013491],
      [114.07508489,  62.66841043],
      [82.84061812,   71.74110339],
      [49.57522829,   75.76762688],
      [153.37176487,  62.67037789],
      [180.58877111,  70.74156227],
      [208.82030103,  71.75278198],
      [135.25632113, 127.17084251],
      [123.14381424, 127.18696081],
      [114.07040428, 175.55412537],
      [100.96522807, 216.88775698],
      [148.34837326, 126.17318282],
      [160.44491098, 172.54367428],
      [170.52955213, 213.86912628],
      [135.25650468,  42.51193385],
      [143.30006424,  42.52114882],
      [126.19122843,  42.51358583],
      [146.33472146,  43.5294833],
      [174.54557865, 224.94029919],
      [180.58716501, 221.92157673],
      [168.51536114, 217.89877019],
      [106.02684471, 229.98212647],
      [98.96623761,  228.96643264],
      [97.95422632,  219.9003304]]
)

class Main(Frame):
    def __init__(self):
        super().__init__()

        self.pack(fill=BOTH, expand=1)
        self.canvas = Canvas(self)
        self.canvas.pack(fill=BOTH, expand=1)

        self.load_default_kps()

        # this data is used to keep track of an 
        # item being dragged
        self._drag_data = {"x": 0, "y": 0, "item": None}

        # add bindings for clicking, dragging and releasing over
        # any object with the "token" tag
        self.canvas.tag_bind("token", "<ButtonPress-1>", self.on_token_press)
        self.canvas.tag_bind("token", "<ButtonRelease-1>", self.on_token_release)
        self.canvas.tag_bind("token", "<B1-Motion>", self.on_token_motion)

    def get_kp_positions(self):
        coords = np.array([self.canvas.coords(o) for o in self.ovals])
        x1, y1, x2, y2 = [coords[:, i] for i in [0, 1, 2, 3]]
        x = x1 + (x2 - x1) / 2
        y = y1 + (y2 - y1) / 2
        return np.stack([x, y], -1)

    def load_default_kps(self):
        self.ovals = []
        for i, [x, y] in enumerate(STANDART_KPS):
            hue = 360. * (i / len(STANDART_KPS))
            o = self.canvas.create_oval(x-5, y-5,
                                        x+5, y+5,
                                        fill=rgb2hex(*hsv2rgb(hue, 1, 1)),
                                        outline=None, width=1,
                                        tags=('token', 'kp-{}'.format(i)))
            self.ovals += [o]

        self.bbox = self.canvas.create_rectangle(0, 0,
                                                 255, 255,
                                                 tags='token',
                                                 outline=None, width=3)

    def on_token_press(self, event):
        '''Begining drag of an object'''
        # record the item and its location
        self._drag_data["item"] = self.canvas.find_closest(event.x, event.y)[0]
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def on_token_release(self, event):
        '''End drag of an object'''
        # reset the drag information
        self._drag_data["item"] = None
        self._drag_data["x"] = 0
        self._drag_data["y"] = 0

        print(self.get_kp_positions())

    def on_token_motion(self, event):
        '''Handle dragging of an object'''
        # compute how much the mouse has moved
        delta_x = event.x - self._drag_data["x"]
        delta_y = event.y - self._drag_data["y"]
        # move the object the appropriate amount
        self.canvas.move(self._drag_data["item"], delta_x, delta_y)

        if self._drag_data['item'] == self.bbox:
            for o in self.ovals:
                self.canvas.move(o, delta_x, delta_y)
        # record the new position
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y


import math

def hsv2rgb(h, s, v):
    h = float(h)
    s = float(s)
    v = float(v)
    h60 = h / 60.0
    h60f = math.floor(h60)
    hi = int(h60f) % 6
    f = h60 - h60f
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    r, g, b = 0, 0, 0
    if hi == 0: r, g, b = v, t, p
    elif hi == 1: r, g, b = q, v, p
    elif hi == 2: r, g, b = p, v, t
    elif hi == 3: r, g, b = p, q, v
    elif hi == 4: r, g, b = t, p, v
    elif hi == 5: r, g, b = v, p, q
    r, g, b = int(r * 255), int(g * 255), int(b * 255)
    return r, g, b
    
def rgb2hsv(r, g, b):
    r, g, b = r/255.0, g/255.0, b/255.0
    mx = max(r, g, b)
    mn = min(r, g, b)
    df = mx-mn
    if mx == mn:
        h = 0
    elif mx == r:
        h = (60 * ((g-b)/df) + 360) % 360
    elif mx == g:
        h = (60 * ((b-r)/df) + 120) % 360
    elif mx == b:
        h = (60 * ((r-g)/df) + 240) % 360
    if mx == 0:
        s = 0
    else:
        s = df/mx
    v = mx
    return h, s, v

def clamp(x): 
      return max(0, min(x, 255))

def rgb2hex(r, g, b):
  return "#{0:02x}{1:02x}{2:02x}".format(clamp(r), clamp(g), clamp(b))


def main():

    root = Tk()
    ex = Main()
    root.geometry("500x500+0+0")
    root.mainloop()


if __name__ == '__main__':
    main()
