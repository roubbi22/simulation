from dataclasses import dataclass
from typing import Union, Literal

import math
import numpy as np

@dataclass
class EndVector:
    x: float
    y: float
    angle: float
    
    def __add__(self, other: EndVector):
        if isinstance(other, tuple) and len(other) == 3:
            return EndVector(self.x + other[0], self.y + other[1], self.angle + other[2])
        elif isinstance(other, EndVector):
            return EndVector(self.x + other.x, self.y + other.y, self.angle + other.angle)
        return NotImplemented
    
    def __sub__(self, other: EndVector):
        if isinstance(other, tuple) and len(other) == 3:
            return EndVector(self.x - other[0], self.y - other[1], self.angle - other[2])
        elif isinstance(other, EndVector):
            return EndVector(self.x - other.x, self.y - other.y, self.angle - other.angle)
        return NotImplemented
    
    def __mul__(self, scalar):
        return EndVector(self.x * scalar, self.y * scalar, self.angle)
    
    def __truediv__(self, scalar: float):
        return EndVector(self.x / scalar, self.y / scalar, self.angle)
    
    def rotate(self, rotation_center: Union[tuple, EndVector], angle, unit: Literal["rad", "deg"] = "deg"):
        # define rotation matrix
        alpha = np.radians(angle) if unit == "deg" else angle
        if isinstance(rotation_center, tuple):
            c_x, c_y = rotation_center
        else:
            c_x = rotation_center.x
            c_y = rotation_center.y

        cossine, sine = np.cos(alpha), np.sin(alpha)

        rotation_matrix = np.array([
            [np.cos(alpha), -np.sin(alpha), c_x - c_x * cossine + c_y * sine],
            [np.sin(alpha), np.cos(alpha), c_y - c_x * sine - c_y * cossine],
            [0, 0, 1]
        ])

        end_vector = np.array([
            self.x,
            self.y,
            1
        ])

        end_vector_rotated = rotation_matrix @ end_vector

        self.x = round(end_vector_rotated[0], 2)
        self.y = round(end_vector_rotated[1], 2)
        self.angle = (self.angle + (angle if unit == "deg" else np.degrees(angle))) % 360
        

    def calc_dist_to_other(self, other: EndVector) -> list[float]:
        return [
            math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2),
            (self.angle - other.angle) % 360
        ]