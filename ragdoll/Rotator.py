import numpy as np
from numpy.linalg import norm
from skimage.transform import SimilarityTransform


class Rotator:
    def __init__(self, canvas, selection_getter, managed_widgets):
        self.canvas = canvas
        self.get_selection = selection_getter
        self.others = managed_widgets

        self.canvas.bind("<Button-1>", self.maybe_rotate, '+')
        self.canvas.bind("<Button-3>", self.set_center, '+')
        self.canvas.bind("<Double-Button-3>", self.unset_center, '+')
        self.canvas.bind("<B1-Motion>", self.maybe_rotate, '+')
        self.canvas.bind("<ButtonRelease-1>", self.stop, '+')

        self._drag_data = {"x": 0, "y": 0}
        self.active = True
        self.go = False
        self.rotation_center = None

    def unset_center(self, event):
        self.rotation_center = None

    def set_center(self, event):
        self.rotation_center = np.array([event.x, event.y])

    def maybe_rotate(self, event):
        if self.active and (self.go or self.event_inside_rotate_radius(event)):
            for o in self.others:
                o.active = False

            self.rotate_selection(event)
            self.go = True

    def stop(self, event):
        if self.active:
            for o in self.others:
                o.active = True
            self.go = False

    def rotate_selection(self, event):
        selection = self.get_selection()
        sel_pos = np.array([self.canvas.coords(s) for s in selection])
        sel_pos = sel_pos[..., :2] + (sel_pos[..., 2:] - sel_pos[..., :2]) / 2

        sel_center = np.mean(sel_pos, axis=0)
        if self.rotation_center is not None:
            sel_center = self.rotation_center

        pos_old = np.array([self._drag_data["x"], self._drag_data["y"]])
        if np.all(pos_old == np.array([0, 0])):
            pos_old = np.array([event.x, event.y])
        direction_old = pos_old - sel_center

        pos_new = np.array([event.x, event.y])
        direction_new = pos_new - sel_center

        X = np.array([direction_new[0], direction_old[0]])
        Y = np.array([direction_new[1], direction_old[1]])

        angle = np.arctan2(Y, X)
        angle = angle[1] - angle[0]

        rot_trans = SimilarityTransform(rotation=angle)
        new_coords = rot_trans.inverse(sel_pos - sel_center) + sel_center

        for s, old, new in zip(selection, sel_pos, new_coords):
            delta_x = new[0] - old[0]
            delta_y = new[1] - old[1]
            self.canvas.move(s, delta_x, delta_y)

        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def event_inside_rotate_radius(self, event):
        x, y = event.x, event.y
        selection = self.get_selection()
        if len(selection) == 0:
            return False

        sel_pos = np.array([self.canvas.coords(s) for s in selection])
        sel_pos = sel_pos[..., :2] + (sel_pos[..., 2:] - sel_pos[..., :2]) / 2

        bbox = np.array(list(sel_pos.min(0)) + list(sel_pos.max(0)))

        sel_center = np.mean(sel_pos, axis=0)

        x_in = x <= bbox[2] + 20 and x >= bbox[0] - 20
        y_in = y <= bbox[3] + 20 and y >= bbox[1] - 20

        return x_in and y_in
