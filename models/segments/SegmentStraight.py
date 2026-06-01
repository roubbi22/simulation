from custom_types.EndVector import EndVector
from models.segments import BaseSegment
from view import ItemSegmentStraight
from typing import Union, Literal, TYPE_CHECKING

from models.segments import SegmentEnd

if TYPE_CHECKING:
    from models.Track import Track

class SegmentStraight(BaseSegment):
    def __init__(self, track: "Track", length, coords: list, starting_end:Literal["a", "b"]="a", **kwargs):
        super().__init__(
            track=track,
            starting_end=starting_end,
            **kwargs
        )
        self.metadata = {
            **self.metadata,
            "length_a.b": length,
            "coords": coords,
        }
        self.length = length
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
    
    def get_opposite_end(self, end: SegmentEnd):
        if end.get_end_id().split(".")[1] == "a":
            return self.ends["b"]
        return self.ends["a"]
    
    def move_by_distance(self, from_end: Union[str, SegmentEnd], previous_percentage: float, distance = 0):
        from_end_key = from_end
        if isinstance(from_end, SegmentEnd): 
            for k, v in self.ends.items():
                if v is from_end:
                    from_end_key = k
        else:
            from_end = self.ends[from_end_key]

        remaining_segment_distance = self.length * (1 - previous_percentage)
        to_end_key = "b" if from_end_key == "a" else "a"
        to_end = self.ends[to_end_key]
        if distance > remaining_segment_distance:
            return to_end.connected_to.parent_segment.move_by_distance(to_end.connected_to, 0, distance - remaining_segment_distance)
        elif distance < 0 and self.length-remaining_segment_distance:
            return from_end.connected_to.parent_segment.move_by_distance(
                from_end.connected_to.parent_segment.get_opposite_end(from_end.connected_to),
                1,
                distance + (previous_percentage * self.length))
        new_percentage = previous_percentage + (distance / self.length)
        return (self, from_end_key, to_end_key, new_percentage)

    def update_view(self):
        return super().update_view()