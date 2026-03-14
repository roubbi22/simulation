from typing import Tuple
from models.segments import BaseSegment
from custom_types.EndVector import EndVector
from view import ItemVehicle

class Vehicle:
    def __init__(self, scene, segment: BaseSegment, from_end: str, to_end: str, percentage: float = 0):
        self.position: Tuple[BaseSegment, str, str, float] = (segment, from_end, to_end, percentage) # Segment, from_end, to_end, percentage
        self.speed: 0
        self.coords: EndVector = segment.get_coordinates_on_segment(from_end, to_end, percentage)
        self.graphical_representation: ItemVehicle = ItemVehicle(scene, self)

    def move(self):
        pass