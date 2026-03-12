from PyQt6.QtWidgets import QGraphicsScene
from models.segments import BaseSegment, SegmentStraight , SegmentCurve, SegmentSwitch, SegmentEnd
from custom_types.SegmentTypes import SegmentType
from typing import Dict
import uuid
import json

class Track:
    def __init__(self, scene: QGraphicsScene):
        self.scene = scene
        self.segments: Dict[str, BaseSegment] = {}
        self.altered_since_save = True
        self.file_path = None
        
    def add_segment(
            self,
            segment_id: str = None,
            segment_end: SegmentEnd = None,
            coords: list = None,
            new_segment_starting_end: str = "a",
            segment_type: SegmentType = "Gerade",
            **kwargs
        ):
        """
        adds a new segment to the track
        """
        if not segment_id:
            segment_id = str(uuid.uuid4())

        print(kwargs)

        if coords:
            match segment_type:
                case "Gerade": new_segment = SegmentStraight(self, kwargs.get("length", 200), coords, starting_end=new_segment_starting_end)
                case "Kurve links": new_segment = SegmentCurve(self, coords, kwargs.get("radius", 400), kwargs.get("angle", 30), kwargs.get("dir", "l"), starting_end=new_segment_starting_end)
                case "Kurve rechts": new_segment = SegmentCurve(self, coords, kwargs.get("radius", 400), kwargs.get("angle", 30), kwargs.get("dir", "r"), starting_end=new_segment_starting_end)
                case "Weiche links": new_segment = SegmentSwitch(self, coords, kwargs.get("length", 200), kwargs.get("radius", 400), kwargs.get("angle", 30), kwargs.get("dir", "l"), starting_end=new_segment_starting_end)
                case "Weiche rechts": new_segment = SegmentSwitch(self, coords, kwargs.get("length", 200), kwargs.get("radius", 400), kwargs.get("angle", 30), kwargs.get("dir", "r"), starting_end=new_segment_starting_end)

            if segment_end:
                segment_end.connected_to = new_segment.ends[new_segment_starting_end]
                new_segment.ends[new_segment_starting_end].connected_to = segment_end
                segment_end.parent_segment.update_view()
                new_segment.update_view()
            self.segments[segment_id] = new_segment
            
            for end in new_segment.ends.values():
                if not end.connected_to:
                    matching_ends = self.check_overlapping_ends(end)
                    for matching_end in matching_ends:
                        matching_end.connected_to = end
                        end.connected_to = matching_end
                        matching_end.parent_segment.update_view()
                        end.parent_segment.update_view()

            self.altered_since_save = True

    def check_overlapping_ends(self, end_to_check: SegmentEnd, dist_tolerance=0.5, angle_tolerance=3) -> list[SegmentEnd]:
        # return list of overlapping Segment ends
        matching_ends = []
        open_ends = self._get_open_ends()
        for open_end in open_ends:
            if open_end is not end_to_check:
                distance, angle  = end_to_check.vector.calc_dist_to_other(open_end.vector)
                if distance < dist_tolerance and abs((180 - angle) % 360) < angle_tolerance:
                    matching_ends.append(open_end)
        return matching_ends
        
    def remove_segment(self, segment: "BaseSegment"):
        for end in segment.ends.values():
            if(end.connected_to):
                end.connected_to.connected_to = None
                end.connected_to.graphic_representation = None
                end.connected_to.parent_segment.update_view()
        self.segments = {k: v for k, v in self.segments.items() if v != segment}
        self.scene.removeItem(segment.graphical_representation)
        self.altered_since_save = True

    def _get_open_ends(self) -> list[SegmentEnd]:
        open_ends = []
        for segment in self.segments.values():
            for end in segment.ends.values():
                if end.connected_to is None:
                    open_ends.append(end)

        return open_ends

    def store(self, file_path):
        """
        store the track to .json file
        """
        ouput= {}

        for key, segment in self.segments.items():

            ouput[key] = {}

            if isinstance(segment, SegmentStraight):
                segment_type = "st"
            elif isinstance(segment, SegmentCurve) and segment.dir == "l":
                segment_type = "cl"
            elif isinstance(segment, SegmentCurve) and segment.dir == "r":
                segment_type = "cr"
            elif isinstance(segment, SegmentSwitch) and segment.dir == "l":
                segment_type = "sl"
            elif isinstance(segment, SegmentSwitch) and segment.dir == "r":
                segment_type = "sr"

            connections = {}
            location = {}

            for end_key, end in segment.ends.items():
                if end.connected_to == None:
                    connections[end_key] = None
                else:
                    other_parent_key = next((k for k, v in self.segments.items() if v is end.connected_to.parent_segment))
                    other_end_key = next((ok for ok, ov in self.segments[other_parent_key].ends.items() if ov is end.connected_to))
                    connections[end_key] = f"{other_parent_key}.{other_end_key}"
                location[end_key] = [end.vector.x, -end.vector.y]

            ouput[key]["type"] = segment_type
            ouput[key]["connections"] = connections
            ouput[key]["location"] = location
            ouput[key]["metadata"] = segment.metadata

        with open(file_path, "w") as file:
            json.dump({"segments": ouput}, file, indent=4)

        self.altered_since_save = False

    def open_file(self, file_path):
        """
        load track from file
        """
        
        with open(file_path) as file:
            data = json.load(file)

        new_segments = data["segments"]

        print(file.__dict__.values())
        for segment in self.segments.values():
            self.scene.removeItem(segment.graphical_representation)
        
        self.segments = {}

        segment_types = {
            "st": "Gerade",
            "cl": "Kurve links",
            "cr": "Kurve rechts",
            "sl": "Weiche links",
            "sr": "Weiche rechts",
        }

        for key, segment in new_segments.items():

            add_segment_kwargs = {
                "segment_id": key,
                "coords": segment["metadata"]["coords"],
                "segment_type": segment_types[segment["type"]],
                "new_segment_starting_end": segment["metadata"].get("starting_end", "a"),
            }

            additional_kwargs = {
                "length": segment["metadata"].get("length", None),
                "radius": segment["metadata"].get("radius", None),
                "angle": segment["metadata"].get("angle", None),
                "dir": segment["metadata"].get("dir", None),
            }

            for kwarg_key, kwarg_value in additional_kwargs.items():
                if kwarg_value:
                    add_segment_kwargs[kwarg_key] = kwarg_value

            print(add_segment_kwargs.values())

            self.add_segment(
                **add_segment_kwargs
            )

        self.altered_since_save = False