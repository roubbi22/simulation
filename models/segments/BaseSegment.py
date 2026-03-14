from abc import ABC, abstractmethod
from custom_types.EndVector import EndVector
from view import GraphicBaseSegment
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.Track import Track
    from models.segments import SegmentEnd

class BaseSegment(ABC):
    def __init__(self, track: "Track", starting_end = "a"):
        self.track: "Track" = track
        self.ends: dict[str, "SegmentEnd"] = {}
        self.graphical_representation: GraphicBaseSegment = None
        self.starting_end = starting_end
        self.metadata = {
            "starting_end": starting_end
        }     

    @abstractmethod
    def update_view(self):
        if self.graphical_representation:
            self.graphical_representation.update_from_model()

    @abstractmethod
    def translate(self, x, y):
        pass
    
    @abstractmethod
    def rotate(self, angle, anchor: str=None):
        c_x = self.ends[anchor].vector.x if anchor else 0
        c_y = self.ends[anchor].vector.y if anchor else 0

        for end in self.ends.values():
            end.vector.rotate((c_x, c_y), angle)
        
    @abstractmethod
    def connect(self, segment_end_id: str):
        pass

    @abstractmethod
    def get_coordinates_on_segment(self, from_end: str, to_end: str, percentage: float) -> EndVector:
        pass

    def _reposition_for_end(self):
        if self.starting_end != "a":
            self.translate(
                self.ends["a"].vector.x - self.ends[self.starting_end].vector.x,
                self.ends["a"].vector.y - self.ends[self.starting_end].vector.y
            )
            self.rotate(
                self.ends["a"].vector.angle - self.ends[self.starting_end].vector.angle,
                self.starting_end
            )