import networkx as nx
import threading
from typing import Dict, TypedDict, TYPE_CHECKING

from models.segments import SegmentSwitch
from models.segments.BaseSegment import BaseSegment
from vehicle import Vehicle

if TYPE_CHECKING:
    from models.Track import Track 

class VehicleControllerVehicle(TypedDict):
    vehicle: Vehicle
    destination_node: str
    last_segment: BaseSegment | None
    route: list[str]
    arriving: bool


class VehicleController():
    """
    has control over all autonomously controled vehicles
    for each vehicle stores the route
    controlles the target speeds of all vehicles
    also includes the track as graph
    """
    def __init__(self, track: "Track"):
        self.track = track
        self.track.vehicle_controller = self 
        self.track_graph: nx.Graph = self.track.get_track_graph()
        self.vehicles: Dict[
            str,
            VehicleControllerVehicle
        ] = {}
        self.lock = threading.Lock()

    def update_track(self):
        self.track_graph = self.track.get_track_graph()

    def add_vehicle(self, vehicle: Vehicle, vehicle_id: str):
        with self.lock:
            destination_node = self.track.get_random_end(return_type="end_id")
            self.vehicles[vehicle_id] = {
                "vehicle": vehicle,
                "destination_node": destination_node,
                "last_segment": None,
                "route": self._get_best_route(
                    vehicle.position[0].ends[vehicle.position[1]].get_end_id(True),
                    destination_node,
                ),
                "arriving": False,
            }

    def _get_best_route(self, origin_node_id, destination_node_id):
        path = nx.shortest_path(self.track_graph, origin_node_id, destination_node_id)

        prev_ids = ""
        segment_ids = []
        for vehicle_key in self.vehicles.keys():
            for segment_ends_ids in self.vehicles[vehicle_key]["route"]:
                if len(prev_ids) > 0:
                    if prev_ids.split("_")[0].split(".")[0] in segment_ends_ids:
                        segment_ids.append(prev_ids.split("_")[0].split(".")[0])
                    else: segment_ids.append(prev_ids.split("_")[1].split(".")[0])
                prev_ids = segment_ends_ids

        for segment in self.track.segments.values():
            segment.annotated = False
            segment.update_view()
        for segment_id in segment_ids:
            self.track.segments[segment_id].annotated = True
            self.track.segments[segment_id].update_view()

        return path

    
    def control(self):
        with self.lock:
            for vehicle in self.vehicles.values():
                if vehicle["vehicle"].position[0] is not vehicle["last_segment"]:

                    for i in range(len(vehicle["route"]) -1, -1, -1):
                        segment_end_ids = vehicle["route"][i - 1].split("_") + vehicle["route"][i].split("_")
                        seen_segments = set()
                        ends = {}

                        for segment_end_id in segment_end_ids:
                            if segment_end_id.split(".")[0] in seen_segments:
                                duplicate_segment_id = segment_end_id.split(".")[0]
                                duplicate_segment_end_ids = [segment_end_id.split(".")[1], ends[segment_end_id.split(".")[0]]]
                            if segment_end_id != "end":
                                ends[segment_end_id.split(".")[0]] = segment_end_id.split(".")[1]
                            seen_segments.add(segment_end_id.split(".")[0])
                            # print(seen_segments)

                        print(duplicate_segment_id)
                        switch_segment: BaseSegment = self.track.segments[duplicate_segment_id]
                        if isinstance(switch_segment, SegmentSwitch):
                            if "c" in duplicate_segment_end_ids:
                                switch_segment.switch_setting = "c"
                            elif "b" in duplicate_segment_end_ids:
                                switch_segment.switch_setting = "b"

                    if vehicle["arriving"]:
                        return vehicle["vehicle"].set_target_speed(0)
                    v_t_speed = vehicle["vehicle"].target_speed
                    v_pos = vehicle["vehicle"].position
                    if v_pos[0].ends[v_pos[2]].get_end_id(True) == vehicle["route"][-1]:
                        vehicle["arriving"] = True
                    origin_end_id = v_pos[0].ends[v_pos[2 if v_t_speed < 0 else 1]].get_end_id(True)
                    vehicle["route"] = self._get_best_route(
                        origin_end_id,
                        vehicle["destination_node"],
                    )
                    next_edge_id = v_pos[0].ends[v_pos[1 if v_t_speed < 0 else 2]].get_end_id(True)
                    if next_edge_id not in set(vehicle["route"]):
                        if v_t_speed > 0:
                            vehicle["vehicle"].set_target_speed(-200)
                        else:
                            vehicle["vehicle"].set_target_speed(200)


                    vehicle["last_segment"] = vehicle["vehicle"].position[0]

