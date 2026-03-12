from models.segments import BaseSegment
from view import ItemSegmentCurve
from typing import Literal, TYPE_CHECKING
from models.segments import SegmentEnd
import math
import numpy as np

if TYPE_CHECKING:
    from models.Track import Track

class SegmentCurve(BaseSegment):
    def __init__(self, track: "Track", coords: list, radius = 400, angle = 30, dir: Literal["l", "r"] = "l", starting_end:Literal["a", "b"]="a"):
        super().__init__(track, starting_end)
        self.metadata = {
            **self.metadata,
            "radius": radius,
            "angle": angle,
            "dir": dir,
            "coords": coords,
        }
        self.ends = {
            "a": SegmentEnd((0, 0, 0), self),
            "b": SegmentEnd((
                    ((1 - math.cos(np.radians(angle))) * radius) if dir == "l" else (-(1 - math.cos(np.radians(angle))) * radius),
                    radius / 2,
                    (180 - angle) if dir == "l" else (180 + angle)
                ),
                self)
        }
        self.radius = radius,
        self.angle = angle
        self.dir = dir

        self.translate(coords[0], coords[1])
        self.rotate(coords[2] + 180, "a")

        self._reposition_for_end()

        self.graphical_representation = ItemSegmentCurve(
            self,
            track.scene
        )

    def translate(self, x, y):
        for end in self.ends.values():
            end.vector = end.vector + (x, y, 0)
    
    def rotate(self, angle, anchor: Literal["a", "b"] = None):
        return super().rotate(angle, anchor)

    def connect(segment_end_id: str):
        pass

    def update_view(self):
        return super().update_view()