from typing import Any, Tuple
from models.segments import BaseSegment
from custom_types.EndVector import EndVector
from view import ItemVehicle

class Vehicle:
    def __init__(self, scene, segment: BaseSegment, from_end: str, to_end: str, percentage: float = 0, locomotive_length: float = 50, wagons_front: list[list[float | EndVector | None]] = None, wagons_rear: list[list[float | EndVector | None]] = None):
        self.position: Tuple[BaseSegment, str, str, float] = (segment, from_end, to_end, percentage) # Segment, from_end, to_end, percentage
        self.speed: float = 0
        self.target_speed: float = 0 # mm/s
        self.acceleration = 2000 # mm/s^2
        self.coords: EndVector = segment.get_coordinates_on_segment(from_end, to_end, percentage)
        self.previous_tag: str | None = None
        self.locomotive_length = 50
        self.wagons_front = wagons_front if wagons_front else [] 
        self.wagons_rear = wagons_rear if wagons_rear else [] 
        self.wagon_spacing = 5
        self.train_length = {
            "front": self.locomotive_length/2 + sum([wagon[0] for wagon in self.wagons_front]) + self.wagon_spacing * len(self.wagons_front),
            "rear": self.locomotive_length/2 + sum([wagon[0] for wagon in self.wagons_rear]) + self.wagon_spacing * len(self.wagons_rear),
        }
        self.graphical_representation: ItemVehicle = ItemVehicle(scene, self)

    def update(self, delta_t):
        self.simulate(delta_t=delta_t)
        
    def simulate(self, delta_t):
        if abs(self.speed - self.target_speed) < abs(self.acceleration * delta_t):
            self.speed = self.target_speed
        elif((self.target_speed - 0.5) > self.speed ):
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

        prev_position = tuple(self.position)
        self.position = self.position[0].move_by_distance(self.position[1], self.position[3], distance)

        # if self.previous_tag is None:
        #     from_connected_segment = self.position[0].ends[self.position[1]].connected_to.parent_segment if self.position[0].ends[self.position[1]].connected_to else None
        #     from_connected_end = self.position[0].ends[self.position[1]].connected_to.get_end_id().split(".")[1] if self.position[0].ends[self.position[1]].connected_to else None
        #     from_connected_opposite_end = from_connected_segment.get_opposite_end(self.position[0].ends[self.position[1]].connected_to).get_end_id().split(".")[1] if self.position[0].ends[self.position[1]].connected_to else None


            # self.previous_tag = f"{from_connected_segment.get_key()}.{from_connected_opposite_end}_{from_connected_end}" if from_connected_segment and from_connected_opposite_end else f"{self.position[0].get_key()}.{self.position[1]}_{self.position[0].get_key()}.{self.position[2]}"
            # print(f"Vehicle initial position: {self.previous_tag}")
        if (prev_position[0] is self.position[0] and prev_position[3] < 0.5 and self.position[3] >= 0.5):
            self.previous_tag = f"{self.position[0].get_key()}.{self.position[1]}_{self.position[2]}"
            print(f"Vehicle passed midpoint of segment {self.position[0].get_key()}.{self.position[1]}_{self.position[2]}")
        elif (prev_position[0] is self.position[0] and prev_position[3] >= 0.5 and self.position[3] < 0.5):
            self.previous_tag = f"{self.position[0].get_key()}.{self.position[2]}_{self.position[1]}"
            print(f"Vehicle passed midpoint of segment {self.position[0].get_key()}.{self.position[2]}_{self.position[1]}")

        self.coords = self.position[0].get_coordinates_on_segment(self.position[1], self.position[2], self.position[3])

        # iterate through wagons and calculate their positions based on locomotive and accumulative length
        accumulative_front_length = self.locomotive_length/2
        for n, wagon in enumerate(self.wagons_front):
            wagon_length, _ = wagon
            wagon_position: Tuple[BaseSegment, Any, Any, float] =self.position[0].move_by_distance(self.position[1], self.position[3], accumulative_front_length + wagon_length/2 + self.wagon_spacing * (n+1))
            wagon_coords: EndVector = wagon_position[0].get_coordinates_on_segment(wagon_position[1], wagon_position[2], wagon_position[3])
            wagon[1] = wagon_coords
            accumulative_front_length += wagon_length
        accumulative_rear_length = self.locomotive_length/2
        for n, wagon in enumerate(self.wagons_rear):
            wagon_length, _ = wagon
            wagon_position: Tuple[BaseSegment, Any, Any, float] = self.position[0].move_by_distance(self.position[1], self.position[3], -(accumulative_rear_length + wagon_length/2 + self.wagon_spacing * (n+1)))
            wagon_coords: EndVector = wagon_position[0].get_coordinates_on_segment(wagon_position[1], wagon_position[2], wagon_position[3])
            wagon[1] = wagon_coords
            accumulative_rear_length += wagon_length


        self.graphical_representation = ItemVehicle(scene, self)
        self.graphical_representation.update_from_model()
        if scene:
            scene.update()

    def set_target_speed(self, target_speed):
        self.target_speed = target_speed