# from abc import ABC, abstractmethod
# from dataclasses import dataclass
# from typing import Literal, Union, Dict
# from PyQt6.QtWidgets import QGraphicsPathItem, QGraphicsScene
# import numpy as np
# import uuid
# import math
# import json


# from models.segments.BaseSegment import BaseSegment
# from models.segments.SegmentStraight import SegmentStraight
# from view import ItemSegmentStraight, ItemSegmentCurve, ItemSegmentSwitch, GraphicBaseSegment

# type SegmentType = Literal[
#     "Gerade",
#     "Kurve links",
#     "Kurve rechts",
#     "Weiche links",
#     "Weiche rechts",
# ]

# track
# class Track:
#     def __init__(self, scene: QGraphicsScene):
#         self.scene = scene
#         self.segments: Dict[str, "BaseSegment"] = {}
#         self.altered_since_save = True
#         self.file_path = None
        

#     def add_segment(
#             self,
#             segment_id: str = None,
#             segment_end: SegmentEnd = None,
#             coords: list = None,
#             new_segment_starting_end: str = "a",
#             segment_type: SegmentType = "Gerade",
#             **kwargs
#         ):
#         """
#         adds a new segment to the track
#         """
#         if not segment_id:
#             segment_id = str(uuid.uuid4())

#         print(kwargs)

#         if coords:
#             match segment_type:
#                 case "Gerade": new_segment = SegmentStraight(self, kwargs.get("length", 200), coords, starting_end=new_segment_starting_end)
#                 case "Kurve links": new_segment = SegmentCurve(self, coords, kwargs.get("radius", 400), kwargs.get("angle", 30), kwargs.get("dir", "l"), starting_end=new_segment_starting_end)
#                 case "Kurve rechts": new_segment = SegmentCurve(self, coords, kwargs.get("radius", 400), kwargs.get("angle", 30), kwargs.get("dir", "r"), starting_end=new_segment_starting_end)
#                 case "Weiche links": new_segment = SegmentSwitch(self, coords, kwargs.get("length", 200), kwargs.get("radius", 400), kwargs.get("angle", 30), kwargs.get("dir", "l"), starting_end=new_segment_starting_end)
#                 case "Weiche rechts": new_segment = SegmentSwitch(self, coords, kwargs.get("length", 200), kwargs.get("radius", 400), kwargs.get("angle", 30), kwargs.get("dir", "r"), starting_end=new_segment_starting_end)

#             if segment_end:
#                 segment_end.connected_to = new_segment.ends[new_segment_starting_end]
#                 new_segment.ends[new_segment_starting_end].connected_to = segment_end
#                 segment_end.parent_segment.update_view()
#                 new_segment.update_view()
#             self.segments[segment_id] = new_segment
            
#             for end in new_segment.ends.values():
#                 if not end.connected_to:
#                     matching_ends = self.check_overlapping_ends(end)
#                     for matching_end in matching_ends:
#                         matching_end.connected_to = end
#                         end.connected_to = matching_end
#                         matching_end.parent_segment.update_view()
#                         end.parent_segment.update_view()

#             self.altered_since_save = True

#     def check_overlapping_ends(self, end_to_check: SegmentEnd, dist_tolerance=0.5, angle_tolerance=3) -> list[SegmentEnd]:
#         # return list of overlapping Segment ends
#         matching_ends = []
#         open_ends = self._get_open_ends()
#         for open_end in open_ends:
#             if open_end is not end_to_check:
#                 distance, angle  = end_to_check.vector.calc_dist_to_other(open_end.vector)
#                 # print("distance: ", distance, "angle: ", abs((180 - angle) % 360))
#                 if distance < dist_tolerance and abs((180 - angle) % 360) < angle_tolerance:
#                     matching_ends.append(open_end)
#         return matching_ends
        
#     def remove_segment(self, segment: "BaseSegment"):
#         for end in segment.ends.values():
#             # print("--->end: ", end.__dict__.items())
#             if(end.connected_to):
#                 end.connected_to.connected_to = None
#                 end.connected_to.graphic_representation = None
#                 end.connected_to.parent_segment.update_view()
#         self.segments = {k: v for k, v in self.segments.items() if v != segment}
#         self.scene.removeItem(segment.graphical_representation)
#         self.altered_since_save = True

#     def _get_open_ends(self) -> list[SegmentEnd]:
#         open_ends = []
#         for segment in self.segments.values():
#             for end in segment.ends.values():
#                 if end.connected_to is None:
#                     open_ends.append(end)

#         return open_ends

#     def store(self, file_path):
#         """
#         store the track to .json file
#         """
#         ouput= {}

#         for key, segment in self.segments.items():

#             ouput[key] = {}

#             if isinstance(segment, SegmentStraight):
#                 segment_type = "st"
#             elif isinstance(segment, SegmentCurve) and segment.dir == "l":
#                 segment_type = "cl"
#             elif isinstance(segment, SegmentCurve) and segment.dir == "r":
#                 segment_type = "cr"
#             elif isinstance(segment, SegmentSwitch) and segment.dir == "l":
#                 segment_type = "sl"
#             elif isinstance(segment, SegmentSwitch) and segment.dir == "r":
#                 segment_type = "sr"

#             connections = {}
#             location = {}

#             for end_key, end in segment.ends.items():
#                 if end.connected_to == None:
#                     connections[end_key] = None
#                 else:
#                     other_parent_key = next((k for k, v in self.segments.items() if v is end.connected_to.parent_segment))
#                     other_end_key = next((ok for ok, ov in self.segments[other_parent_key].ends.items() if ov is end.connected_to))
#                     connections[end_key] = f"{other_parent_key}.{other_end_key}"
#                 location[end_key] = [end.vector.x, -end.vector.y]

#             metadata = {}
#             # for k, v in segment.__dict__.items():
#             #     print(k, v)
#             #     metadata[k] = v


#             ouput[key]["type"] = segment_type
#             ouput[key]["connections"] = connections
#             ouput[key]["location"] = location
#             ouput[key]["metadata"] = segment.metadata



#         with open(file_path, "w") as file:
#             json.dump({"segments": ouput}, file, indent=4)

#         self.altered_since_save = False

#     def open_file(self, file_path):
#         """
#         load track from file
#         """

#         with open(file_path) as file:
#             data = json.load(file)

#         new_segments = data["segments"]

#         print(file.__dict__.values())
#         for segment in self.segments.values():
#             self.scene.removeItem(segment.graphical_representation)
        
#         self.segments = {}

#         segment_types = {
#             "st": "Gerade",
#             "cl": "Kurve links",
#             "cr": "Kurve rechts",
#             "sl": "Weiche links",
#             "sr": "Weiche rechts",
#         }

#         for key, segment in new_segments.items():

#             add_segment_kwargs = {
#                 "segment_id": key,
#                 "coords": segment["metadata"]["coords"],
#                 "segment_type": segment_types[segment["type"]],
#                 "new_segment_starting_end": segment["metadata"].get("starting_end", "a"),
#             }

#             additional_kwargs = {
#                 "length": segment["metadata"].get("length", None),
#                 "radius": segment["metadata"].get("radius", None),
#                 "angle": segment["metadata"].get("angle", None),
#                 "dir": segment["metadata"].get("dir", None),
#             }

#             for kwarg_key, kwarg_value in additional_kwargs.items():
#                 if kwarg_value:
#                     add_segment_kwargs[kwarg_key] = kwarg_value

#             print(add_segment_kwargs.values())

#             self.add_segment(
#                 **add_segment_kwargs
#             )

#         self.altered_since_save = False
            


# segments

# end
# EndVector = namedtuple('EndVector', ['x', 'y', 'angle'])
# @dataclass
# class EndVector:
#     x: float
#     y: float
#     angle: float
    
#     def __add__(self, other: EndVector):
#         if isinstance(other, tuple) and len(other) == 3:
#             return EndVector(self.x + other[0], self.y + other[1], self.angle + other[2])
#         elif isinstance(other, EndVector):
#             return EndVector(self.x + other.x, self.y + other.y, self.angle + other.angle)
#         return NotImplemented
    
#     def rotate(self, rotation_center: Union[tuple, EndVector], angle, unit: Literal["rad", "deg"] = "deg"):
#         # define rotation matrix
#         alpha = np.radians(angle) if unit == "deg" else angle
#         if isinstance(rotation_center, tuple):
#             c_x, c_y = rotation_center
#         else:
#             c_x = rotation_center.x
#             c_y = rotation_center.y

#         cossine, sine = np.cos(alpha), np.sin(alpha)

#         rotation_matrix = np.array([
#             [np.cos(alpha), -np.sin(alpha), c_x - c_x * cossine + c_y * sine],
#             [np.sin(alpha), np.cos(alpha), c_y - c_x * sine - c_y * cossine],
#             [0, 0, 1]
#         ])

#         end_vector = np.array([
#             self.x,
#             self.y,
#             1
#         ])

#         end_vector_rotated = rotation_matrix @ end_vector

#         self.x = round(end_vector_rotated[0], 2)
#         self.y = round(end_vector_rotated[1], 2)
#         self.angle = (self.angle + (angle if unit == "deg" else np.degrees(angle))) % 360
        

#     def calc_dist_to_other(self, other: SegmentEnd) -> list[float]:
#         return [
#             math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2),
#             (self.angle - other.angle) % 360
#         ]
        


# class SegmentEnd():
#     def __init__(self, vector: EndVector, parent_segment: "BaseSegment"):
#         self.vector:EndVector  = EndVector(vector[0], vector[1], vector[2])
#         self.connected_to: SegmentEnd = None
#         self.graphic_representation:SegmentEnd = None
#         self.parent_segment: "BaseSegment" = parent_segment

# base
# class BaseSegment(ABC):
#     def __init__(self, track: Track, starting_end = "a"):
#         self.track: Track = track
#         self.ends: dict[str, SegmentEnd] = {}
#         self.graphical_representation: GraphicBaseSegment = None
#         self.starting_end = starting_end
#         self.metadata = {
#             "starting_end": starting_end
#         }
        

#     @abstractmethod
#     def update_view(self):
#         # print(f"graphical representation: {self.graphical_representation}")
#         if self.graphical_representation:
#             self.graphical_representation.update_from_model()

#     @abstractmethod
#     def translate(self, x, y):
#         pass
    
#     @abstractmethod
#     def rotate(self, angle, anchor: str=None):
#         # iterate through all ends
#         c_x = self.ends[anchor].vector.x if anchor else 0
#         c_y = self.ends[anchor].vector.y if anchor else 0

#         # print(f"ends: \n")
#         # for key, end in self.ends.items():
#         #     print(key)
#         #     print(end.__dict__.items())

#         # print("rotating around ", anchor, "cx, cy: ", c_x, c_y)
#         for end in self.ends.values():
#             # if key != anchor:
#             end.vector.rotate((c_x, c_y), angle)
        

#     @abstractmethod
#     def connect(self, segment_end_id: str):
#         pass

#     def _reposition_for_end(self):
#         if self.starting_end != "a":
#             self.translate(
#                 self.ends["a"].vector.x - self.ends[self.starting_end].vector.x,
#                 self.ends["a"].vector.y - self.ends[self.starting_end].vector.y
#                 # 0, 0
#             )
#             self.rotate(
#                 self.ends["a"].vector.angle - self.ends[self.starting_end].vector.angle,
#                 self.starting_end
#             )


# straight

# class SegmentStraight(BaseSegment):
#     def __init__(self, track: Track, length, coords: list, starting_end:Literal["a", "b"]="a"):
#         super().__init__(
#             track=track,
#             starting_end=starting_end)
#         self.metadata = {
#             **self.metadata,
#             "length": length,
#             "coords": coords,
#         }
#         self.ends = {
#             "a": SegmentEnd((0, 0, 0), self),
#             "b": SegmentEnd((0, length, 180), self) 
#         }

#         # match self.starting_end:
#         #     case "a":
#         #         return
#         #     case "b":
#         #         self.translate(self.ends["b"], -length)
#         #         self.rotate(180, "b")

        
#         self.translate(coords[0], coords[1])
#         self.rotate(coords[2] + 180, "a")

#         self._reposition_for_end()

#         self.graphical_representation = ItemSegmentStraight(
#             self,
#             track.scene
#         )

#         # print(f"initialized segment withe ends : \na: {self.ends["a"].vector}\nb: {self.ends["b"].vector}" )
#         # print("segment added at: ", self.ends["a"].vector, self.ends["b"].vector)

#     def translate(self, x, y):
#         for end in self.ends.values():
#             end.vector = end.vector + (x, y, 0)
    
#     def rotate(self, angle, anchor: Literal["a", "b"] = None):
#         return super().rotate(angle, anchor)

#     def connect(segment_end_id: str):
#         pass

#     def update_view(self):
#         return super().update_view()
    
# curve
# class SegmentCurve(BaseSegment):
#     def __init__(self, track: Track, coords: list, radius = 400, angle = 30, dir: Literal["l", "r"] = "l", starting_end:Literal["a", "b"]="a"):
#         super().__init__(track, starting_end)
#         self.metadata = {
#             **self.metadata,
#             "radius": radius,
#             "angle": angle,
#             "dir": dir,
#             "coords": coords,
#         }
#         self.ends = {
#             "a": SegmentEnd((0, 0, 0), self),
#             "b": SegmentEnd((
#                     ((1 - math.cos(np.radians(angle))) * radius) if dir == "l" else (-(1 - math.cos(np.radians(angle))) * radius),
#                     radius / 2,
#                     (180 - angle) if dir == "l" else (180 + angle)
#                 ),
#                 self)
#         }
#         self.radius = radius,
#         self.angle = angle
#         self.dir = dir

#         # if self.starting_end is not "a":
#         #     self.translate(
#         #         -self.ends[self.starting_end].vector.x,
#         #         -self.ends[self.starting_end].vector.y,
#         #     )
#         #     self.rotate(
#         #         -self.ends[self.starting_end].vector.angle,
#         #         self.starting_end
#         #     )
        
#         self.translate(coords[0], coords[1])
#         self.rotate(coords[2] + 180, "a")

#         self._reposition_for_end()

#         self.graphical_representation = ItemSegmentCurve(
#             self,
#             track.scene
#         )

#         # print(f"initialized segment withe ends : \na: {self.ends["a"].vector}\nb: {self.ends["b"].vector}" )
#         # print("segment added at: ", self.ends["a"].vector, self.ends["b"].vector)

#     def translate(self, x, y):
#         for end in self.ends.values():
#             end.vector = end.vector + (x, y, 0)
    
#     def rotate(self, angle, anchor: Literal["a", "b"] = None):
#         return super().rotate(angle, anchor)

#     def connect(segment_end_id: str):
#         pass

#     def update_view(self):
#         return super().update_view()

# switch
# class SegmentSwitch(BaseSegment):
#     def __init__(self, track: Track, coords: list, length=200, radius = 400, angle = 30, dir: Literal["l", "r"] = "l", starting_end:Literal["a", "b", "c"]="a"):
#         super().__init__(track, starting_end)

#         self.metadata = {
#             **self.metadata,
#             "length": length,
#             "radius": radius,
#             "angle": angle,
#             "dir": dir,
#             "coords": coords,
#         }

#         self.ends = {
#             "a": SegmentEnd((0, 0, 0), self),
#             "b": SegmentEnd((0, length, 180), self),
#             "c": SegmentEnd((
#                     ((1 - math.cos(np.radians(angle))) * radius) if dir == "l" else (-(1 - math.cos(np.radians(angle))) * radius),
#                     radius / 2,
#                     (180 - angle) if dir == "l" else (180 + angle)
#                 ),
#                 self)
#         }
#         self.radius = radius,
#         self.angle = angle
#         self.dir = dir
        
#         self.translate(coords[0], coords[1])
#         self.rotate(coords[2] + 180, "a")

#         self._reposition_for_end()

#         self.graphical_representation = ItemSegmentSwitch(
#             self,
#             track.scene
#         )

#     def translate(self, x, y):
#         for end in self.ends.values():
#             end.vector = end.vector + (x, y, 0)
    
#     def rotate(self, angle, anchor: Literal["a", "b", "c"] = None):
#         return super().rotate(angle, anchor)

#     def connect(segment_end_id: str):
#         pass

#     def update_view(self):
#         return super().update_view()

