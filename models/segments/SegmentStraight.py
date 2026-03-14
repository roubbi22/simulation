from custom_types.EndVector import EndVector
from models.segments import BaseSegment
from view import ItemSegmentStraight
from typing import Literal, TYPE_CHECKING

from models.segments import SegmentEnd

if TYPE_CHECKING:
    from models.Track import Track

class SegmentStraight(BaseSegment):
    def __init__(self, track: "Track", length, coords: list, starting_end:Literal["a", "b"]="a"):
        super().__init__(
            track=track,
            starting_end=starting_end)
        self.metadata = {
            **self.metadata,
            "length": length,
            "coords": coords,
        }
        self.ends = {
            "a": SegmentEnd((0, 0, 0), self),
            "b": SegmentEnd((0, length, 180), self) 
        }
        
        self.translate(coords[0], coords[1])
        self.rotate(coords[2] + 180, "a")

        self._reposition_for_end()

        self.graphical_representation = ItemSegmentStraight(
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
        diff_vector = (self.ends[to_end].vector - self.ends[from_end].vector)
        coords = self.ends[from_end].vector + (diff_vector * percentage)
        coords.angle = (self.ends[from_end].vector.angle + 180) % 360 
        return coords

    def update_view(self):
        return super().update_view()