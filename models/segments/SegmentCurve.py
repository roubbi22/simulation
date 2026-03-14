from custom_types.EndVector import EndVector
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
        self.radius = radius
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

    def get_coordinates_on_segment(self, from_end: str, to_end: str, percentage: float) -> EndVector:
        # get the coordinates of the center point
        angle_to_center = self.ends["a"].vector.angle + (90 if self.dir == "l" else -90)
        rot_center = EndVector(
            self.ends["a"].vector.x + (math.sin(np.radians(angle_to_center)) * self.radius),
            self.ends["a"].vector.y - (math.cos(np.radians(angle_to_center)) * self.radius),
            0
        )
        coords = EndVector(
            self.ends[from_end].vector.x,
            self.ends[from_end].vector.y,
            (self.ends[from_end].vector.angle + 180) % 360,
        )
        # rotate the from_end point by the segment angle times percentage depending on from_end and dir
        if (self.dir == "l" and from_end == "a") or (self.dir == "r" and from_end == "b"):
            coords.rotate(rot_center, -self.angle * percentage)
        else: 
            coords.rotate(rot_center, self.angle * percentage)
        return coords
        

    def update_view(self):
        return super().update_view()