from typing import Tuple
from models.segments import BaseSegment
from custom_types.EndVector import EndVector
from view import ItemVehicle

class Vehicle:
    def __init__(self, scene, segment: BaseSegment, from_end: str, to_end: str, percentage: float = 0):
        self.position: Tuple[BaseSegment, str, str, float] = (segment, from_end, to_end, percentage) # Segment, from_end, to_end, percentage
        self.speed: float = 0
        self.target_speed: float = -100 # mm/2
        self.acceleration = 100 # mm/s^2
        self.coords: EndVector = segment.get_coordinates_on_segment(from_end, to_end, percentage)
        self.graphical_representation: ItemVehicle = ItemVehicle(scene, self)

    def update(self, delta_t):
        self.simulate(delta_t=delta_t)
        
    def simulate(self, delta_t):
        if((self.target_speed - 0.5) > self.speed ):
            self.speed = self.speed + self.acceleration * delta_t
        elif((self.target_speed + 0.5) < self.speed ):
            self.speed = self.speed - self.acceleration * delta_t

        self.move(delta_t=delta_t)

    def move(self, distance: float = None, delta_t: float = None):
        if delta_t:
            distance = self.speed * delta_t
        if not distance and not delta_t:
            print("either distance or delta_t must be provided")
        if self.graphical_representation and self.graphical_representation.scene:
            self.graphical_representation.scene.removeItem(self.graphical_representation)
            scene = self.graphical_representation.scene
        else:
            scene = None
        self.position = self.position[0].move_by_distance(self.position[1], self.position[3], distance)
        self.coords = self.position[0].get_coordinates_on_segment(self.position[1], self.position[2], self.position[3])
        self.graphical_representation = ItemVehicle(scene, self)
        self.graphical_representation.update_from_model()
        if scene:
            scene.update()

    def set_target_speed(self, target_speed):
        self.target_speed = target_speed