from PyQt6.QtWidgets import QGraphicsScene
from models.VehicleController import VehicleController
from models.segments import BaseSegment, SegmentStraight , SegmentCurve, SegmentSwitch, SegmentEnd
from vehicle import Vehicle
from custom_types.SegmentTypes import SegmentType
from typing import Dict, Literal
import uuid
import json
import random

import networkx as nx

class Track:
    def __init__(self, scene: QGraphicsScene):
        self.scene = scene
        self.segments: Dict[str, BaseSegment] = {}
        self.vehicles: Dict[str, Vehicle] = {}
        self.altered_since_save = True
        self.file_path = None
        self.vehicle_controller: VehicleController = None
        
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

        if coords:
            match segment_type:
                case "Gerade": new_segment = SegmentStraight(self, kwargs.get("length_a.b", 200), coords, starting_end=new_segment_starting_end)
                case "Kurve links": new_segment = SegmentCurve(self, coords, kwargs.get("radius", 400), kwargs.get("angle", 30), kwargs.get("dir", "l"), starting_end=new_segment_starting_end)
                case "Kurve rechts": new_segment = SegmentCurve(self, coords, kwargs.get("radius", 400), kwargs.get("angle", 30), kwargs.get("dir", "r"), starting_end=new_segment_starting_end)
                case "Weiche links": new_segment = SegmentSwitch(self, coords, kwargs.get("length_a.b", 200), kwargs.get("radius", 400), kwargs.get("angle", 30), kwargs.get("dir", "l"), starting_end=new_segment_starting_end)
                case "Weiche rechts": new_segment = SegmentSwitch(self, coords, kwargs.get("length_a.b", 200), kwargs.get("radius", 400), kwargs.get("angle", 30), kwargs.get("dir", "r"), starting_end=new_segment_starting_end)

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
            self.vehicle_controller.update_track()

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
        self.vehicle_controller.update_track()

    def add_vehicle(self, vehicle: Vehicle):
        vehicle_id = uuid.uuid4()
        self.vehicles[vehicle_id] = vehicle
        self.vehicle_controller.add_vehicle(vehicle, vehicle_id)

    def get_random_end(self, return_type: Literal['end', 'end_id'] = 'end'):
        segment_keys = self.segments.keys()
        random_segment_key = random.choice(list(segment_keys))
        random_segment = self.segments[random_segment_key]
        end_keys = random_segment.ends.keys()
        random_end_key = random.choice(list(end_keys))
        random_end = random_segment.ends[random_end_key]   
        if return_type == 'end_id':
            own_id = random_end.get_end_id()
            other_id = "end" if not random_end.connected_to else random_end.connected_to.get_end_id()
            return f"{own_id}_{other_id}" if other_id == "end" or (own_id < other_id) else f"{other_id}_{own_id}"
        return random_end
    
    def get_segment_by_end_ids(self, from_end_id:str, to_end_id:str):
        segment_end_ids = from_end_id.split("_") + to_end_id.split("_")
        segment_ids = [x.split(".")[0] for x in segment_end_ids]

        seen_segments = set()
        common_segment_id = next(
            (segment_id for segment_id 
             in segment_ids if segment_id in seen_segments or not seen_segments.add(segment_id))
            )
        return self.segments[common_segment_id]

    def _get_open_ends(self) -> list[SegmentEnd]:
        open_ends = []
        for segment in self.segments.values():
            for end in segment.ends.values():
                if end.connected_to is None:
                    open_ends.append(end)

        return open_ends
    
    def _get_segments_dict(self, include_meta: bool = True) -> Dict:
        """
        returns an dict containing all segments
        """
        output= {}

        for key, segment in self.segments.items():

            output[key] = {}

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

            output[key]["type"] = segment_type
            output[key]["connections"] = connections
            output[key]["location"] = location
            if include_meta:
                output[key]["metadata"] = segment.metadata
        
        return output

    def store(self, file_path):
        """
        store the track to .json file
        """
        output = self._get_segments_dict(True)

        with open(file_path, "w") as file:
            json.dump({"segments": output}, file, indent=4)

        self.altered_since_save = False

    def open_file(self, file_path):
        """
        load track from file
        """

        with open(file_path) as file:
            data = json.load(file)

        new_segments = data["segments"]

        self.scene.clear()
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
                "length_a.b": segment["metadata"].get("length_a.b", None),
                "lenght_a.c": segment["metadata"].get("length_a.c", None),
                "radius": segment["metadata"].get("radius", None),
                "angle": segment["metadata"].get("angle", None),
                "dir": segment["metadata"].get("dir", None),
            }

            for kwarg_key, kwarg_value in additional_kwargs.items():
                if kwarg_value:
                    add_segment_kwargs[kwarg_key] = kwarg_value

            self.add_segment(
                **add_segment_kwargs
            )

        self.altered_since_save = False

    def get_track_graph(self) -> nx.Graph:
        segments =self._get_segments_dict(True)

        G = nx.Graph()
        nodes = {}
        edges = []
        pos = {}

        for segment_id, segment in segments.items():
            segment_type = segment["type"]
            segment_meta = segment["metadata"]
            ports: Dict = segment["connections"]

            for port, value in ports.items():
                own: str = f"{segment_id}.{port}"
                other: str = value

                if not value:
                    node_id = f"{own}_end"
                elif(
                    own.split(".")[0] < other.split(".")[0]
                ):
                    node_id = f"{own}_{other}"
                else: node_id = f"{other}_{own}"

                if node_id not in nodes:
                    nodes[node_id] = node_id
                    pos[node_id] = segment["location"][port]
                
                ports[port] = node_id
            
            if segment_type in ("st", "cl", "cr", "sl", "sr"):
                edges.append((ports["a"], ports["b"], {"length": segment_meta["length_a.b"]}))
            else:
                print("segment not found")
            if segment_type in ("sl", "sr"):
                if "c" in ports and ports["c"] is not None:
                    edges.append((ports["a"], ports["c"], {"length": segment_meta["length_a.c"]}))

        G.add_nodes_from(nodes)
        G.add_edges_from(edges)

        return G

        pass

    def simulate(self, delta_t: float = 1/30):
        for vehicle in self.vehicles.values():
            self.vehicle_controller.control()
            vehicle.update(delta_t=delta_t)
