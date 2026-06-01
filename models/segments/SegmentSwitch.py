from custom_types.EndVector import EndVector
from models.segments import BaseSegment, SegmentEnd
from view import ItemSegmentSwitch
from typing import Literal, TYPE_CHECKING
import math
import numpy as np

if TYPE_CHECKING:
    from models.Track import Track

class SegmentSwitch(BaseSegment):
    def __init__(self, track: "Track", coords: list, length=200, radius = 400, angle = 30, dir: Literal["l", "r"] = "l", starting_end:Literal["a", "b", "c"]="a", **kwargs):
        super().__init__(track, starting_end, **kwargs)

        self.metadata = {
            **self.metadata,
            "length_a.b": length,
            "length_a.c": radius * math.pi * (angle / 180),
            "radius": radius,
            "angle": angle,
            "dir": dir,
            "coords": coords,
        }

        self.ends = {
            "a": SegmentEnd((0, 0, 0), self),
            "b": SegmentEnd((0, length, 180), self),
            "c": SegmentEnd((
                    ((1 - math.cos(np.radians(angle))) * radius) if dir == "l" else (-(1 - math.cos(np.radians(angle))) * radius),
                    radius / 2,
                    (180 - angle) if dir == "l" else (180 + angle)
                ),
                self)
        }
        
        self.radius = radius
        self.angle = angle
        self.dir = dir
        self.switch_setting: Literal["b", "c"] = "b"
        self.length_straight = radius / 2
        self.length_curve = math.pi * radius * (angle / 180)
        
        self.translate(coords[0], coords[1])
        self.rotate(coords[2] + 180, "a")

        self._reposition_for_end()

        self.graphical_representation = ItemSegmentSwitch(
            self,
            track.scene
        )

    def translate(self, x, y):
        for end in self.ends.values():
            end.vector = end.vector + (x, y, 0)
    
    def rotate(self, angle, anchor: Literal["a", "b", "c"] = None):
        return super().rotate(angle, anchor)

    def connect(segment_end_id: str):
        pass

    def get_coordinates_on_segment(self, from_end: str, to_end: str, percentage: float):
        if from_end == "c" or to_end == "c":
        # if self.switch_setting == "c":
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
            if (self.dir == "l" and from_end == "a") or (self.dir == "r" and from_end == "c"):
                coords.rotate(rot_center, -self.angle * percentage)
            else: 
                coords.rotate(rot_center, self.angle * percentage)
        else: 
            diff_vector = (self.ends[to_end].vector - self.ends[from_end].vector)
            coords = self.ends[from_end].vector + (diff_vector * percentage)
            coords.angle = (self.ends[from_end].vector.angle + 180) % 360 
        return coords
    
    def toggle_switch_setting(self):
        self.switch_setting = "c" if self.switch_setting == "b" else "b"
        self.graphical_representation.update_from_model()

    def get_opposite_end(self, end: SegmentEnd):
        if end.get_end_id().split(".")[1] == "c" or end.get_end_id().split(".")[1] == "b":
            return self.ends["a"]
        elif self.switch_setting == "b":
            return self.ends["b"]
        return self.ends["c"]

    def move_by_distance(self, from_end: str, previous_percentage: float, distance = 0):
        length = self.length_straight if self.switch_setting == "b" else self.length_curve
        from_end_key = from_end
        if isinstance(from_end, SegmentEnd): 
            for k, v in self.ends.items():
                if v is from_end:
                    from_end_key = k
        else:
            from_end = self.ends[from_end_key]

        remaining_segment_distance = length * (1 - previous_percentage)

        if from_end_key == "b" or from_end_key == "c": to_end_key = "a"
        else: to_end_key = self.switch_setting

        to_end = self.ends[to_end_key]
        if distance > remaining_segment_distance:
            return to_end.connected_to.parent_segment.move_by_distance(to_end.connected_to, 0, distance - remaining_segment_distance)
        elif distance < 0 and abs(distance) > length-remaining_segment_distance:
            return from_end.connected_to.parent_segment.move_by_distance(
                from_end.connected_to.parent_segment.get_opposite_end(from_end.connected_to),
                1,
                distance + (previous_percentage * length))
        new_percentage = previous_percentage + (distance / length)
        return (self, from_end_key, to_end_key, new_percentage)

    def update_view(self):
        return super().update_view()