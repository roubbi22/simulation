import math

import networkx as nx
import threading
from typing import Dict, TypedDict, TYPE_CHECKING

import time

from models.segments import SegmentSwitch
from models.segments.BaseSegment import BaseSegment
from vehicle import Vehicle

# from pathfinding_strategies.Dijkstra import Dijkstra
from strategies.pathfinding import DijkstraRail
import vehicle

VEHICLE_SPEED = 400
VEHICLE_SLOW_SPEED = 20

if TYPE_CHECKING:
    from models.Track import Track 

class VehicleControllerVehicle(TypedDict):
    vehicle: Vehicle
    destination_node: str
    last_segment: BaseSegment | None
    last_tag: str | None
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
        self.track_digraph: nx.DiGraph = self.track.get_track_digraph()
        self.vehicles: Dict[
            str,
            VehicleControllerVehicle
        ] = {}
        self.lock = threading.Lock()

    def update_track(self):
        self.track_graph = self.track.get_track_graph()
        self.track_digraph = self.track.get_track_digraph()

    def add_vehicle(self, vehicle: Vehicle, vehicle_id: str):
        with self.lock:
            destination_node = self.track.get_random_end(return_type="end_id")
            print("destination node", destination_node)
            self.vehicles[vehicle_id] = {
                "vehicle": vehicle,
                "destination_node": destination_node,
                "last_segment": None,
                "route": None,
                "arriving": False,
                "arrived": False,
                "braking_start_time": None,
            }

    def _get_best_route(self, origin_node_id, destination_node_id, initial_orientation: str = "a_b", t_lr: float = 75, t_lf: float = 0, shunting_overrun_penalty: float = 100) -> list[str]:
        print(f"calculating best route from {origin_node_id} to {destination_node_id} with initial orientation {initial_orientation} and t_lr {t_lr}, t_lf {t_lf}, shunting_overrun_penalty {shunting_overrun_penalty}")
        dijkstra = DijkstraRail()

        path = dijkstra.find_path(self.track_digraph, f"{origin_node_id}.", f"{destination_node_id}.", t_lr, t_lf, shunting_overrun_penalty, initial_orientation)

        for segment in self.track.segments.values():
            segment.annotated = False
            segment.update_view()

        # mark only segment ids that actually appear in the path entries
        # path entries look like "<segment_id>.<from_end>_<to_end>"
        segment_ids = []
        for entry in path:
            if not isinstance(entry, str):
                continue
            segment_id = entry.split(".", 1)[0]
            if segment_id and segment_id not in segment_ids:
                segment_ids.append(segment_id)

        for segment_id in segment_ids:
            segment = self.track.segments.get(segment_id)
            if segment is None:
                continue
            segment.annotated = True
            segment.update_view()

        return path
    
    def _get_previous_tag_from_previous_segment(self, segment: BaseSegment, from_end: str, to_end: str):
        if segment.ends[from_end].connected_to is None:
            return f"{segment.get_key()}.{from_end}_{to_end}"
        from_connected_segment = segment.ends[from_end].connected_to.parent_segment
        from_connected_end = segment.ends[from_end].connected_to.get_end_id().split(".")[1]
        from_connected_opposite_end = from_connected_segment.get_opposite_end(segment.ends[from_end].connected_to).get_end_id().split(".")[1]
        return f"{from_connected_segment.get_key()}.{from_connected_opposite_end}_{from_connected_end}"
    
    def _toggle_switches_on_route(self, route: list[str]) -> None:
        rev_route = route[::-1]
        for i in rev_route:
            segment_id = i.split(".")[0]
            segment = self.track.segments.get(segment_id)
            if segment and isinstance(segment, SegmentSwitch):
                ends = i.split(".")[1].split("_")
                # segment.toggle_switch_setting("b" if "b" in ends else "c")
                segment.switch_setting = "b" if "b" in ends else "c"

    # def _calculate_braking_start_time(self, vehicle_speed: float, )

    def control(self):
        with self.lock:
            for vehicle in self.vehicles.values():
                if not vehicle["arrived"]:
                    previous_tag = vehicle["vehicle"].previous_tag
                    vehicle_speed = vehicle["vehicle"].speed
                    route = vehicle["route"]

                    if previous_tag is None:
                        # use from end 
                        segment, from_end, to_end, percentage = vehicle["vehicle"].position
                        if vehicle_speed >= 0:
                            if percentage >= 0.5:
                                previous_tag = f"{segment.get_key()}.{from_end}_{to_end}"
                            else:
                                previous_tag = self._get_previous_tag_from_previous_segment(segment, from_end, to_end)
                        else:
                            if percentage <= 0.5:
                                previous_tag = f"{segment.get_key()}.{to_end}_{from_end}"
                            else:
                                previous_tag = self._get_previous_tag_from_previous_segment(segment, to_end, from_end)  

                    reverse_previous_tag = previous_tag.split(".")[0] + "." + previous_tag.split(".")[1].split("_")[1] + "_" + previous_tag.split(".")[1].split("_")[0]
                    ###

                    if route is None or len(route) == 0 or (previous_tag not in route[0:1] and reverse_previous_tag not in route[0:1]):
                        print(f"(re)calculating route from {previous_tag} to {vehicle['destination_node']}. previous tag not in first route element: {route[0] if route else 'None'}, \n route: {route}")
                        vehicle["route"] = self._get_best_route(
                            vehicle["vehicle"].position[0].get_key(),
                            vehicle["destination_node"].split(".")[0],
                            vehicle["vehicle"].position[1] + "_" + vehicle["vehicle"].position[2],
                            vehicle["vehicle"].train_length["rear"],
                            vehicle["vehicle"].train_length["front"],
                            100,
                            
                        )
                        print("initial route: ", vehicle["route"])
                        continue
                    
                    # print(f"route: {route}\n previous_tag: {previous_tag}\n route[0:2]: {route[0:2]}")
                    # time.sleep(1)
                    # if previous_tag == route[0]:
                    #     # print(f"Vehicle {vehicle['vehicle']} on route, previous tag {previous_tag} matches first route element {route[0]}, setting target speed to {VEHICLE_SPEED}")
                    #     vehicle["vehicle"].set_target_speed(VEHICLE_SPEED)
                    # elif reverse_previous_tag == route[0]:
                    #     # print(f"Vehicle {vehicle['vehicle']} on route, previous tag {previous_tag} matches first route element {route[0]} in reverse direction, setting target speed to {-VEHICLE_SPEED}")
                    #     vehicle["vehicle"].set_target_speed(-VEHICLE_SPEED)

                    if vehicle["arriving"] and abs(vehicle_speed) == VEHICLE_SLOW_SPEED:
                        vehicle["vehicle"].set_target_speed(0)
                        print(f"Vehicle arrived at {vehicle['destination_node']}")
                        vehicle["arrived"] = True
                        vehicle["arriving"] = False
                        continue

                    if vehicle["arriving"] and vehicle["braking_start_time"] is not None and vehicle["vehicle"].target_speed != 0:
                        if time.time_ns()/1e9 >= vehicle["braking_start_time"]:
                            # print(f"Vehicle starting to brake for arrival at {vehicle['destination_node']}")
                            dir = 1 if vehicle_speed > 0 else -1
                            vehicle["vehicle"].set_target_speed(dir * VEHICLE_SLOW_SPEED)
                            continue

                    # if len(route) == 1:
                    self._toggle_switches_on_route(route)

                    # if len(route) > 1 and route[1].split(".")[0] == vehicle["destination_node"].split(".")[0]:
                    #     # if previous_tag == route[0]:
                    #     # get length of segment:
                    #     length = self.track_digraph.nodes.get(previous_tag)["length"]/2 + self.track_digraph.nodes.get(route[1])["length"]/2
                        
                    #     v0 = vehicle_speed#
                    #     a = vehicle["vehicle"].acceleration
                    #     braking_distance = v0**2/(2*a)

                    #     dist_until_braking = length - braking_distance * (1 - 0.1) # 10 percnet safetiy margin
                    #     time_until_braking = dist_until_braking / abs(v0) if abs(v0) > 0 else 0

                    #     print(f"Vehicle approaching destination, length until destination: {length}, current speed: {v0}, braking distance: {braking_distance}, time until braking: {time_until_braking}")
                    #     curr_timestamp = time.time_ns()/1e9
                    #     vehicle["braking_start_time"] = curr_timestamp + time_until_braking
                    #     vehicle["arriving"] = True

                    if len(route) > 1:    
                        # print(f"previous tag: {previous_tag}, reverse previous tag: {reverse_previous_tag}")
                        if vehicle_speed == 0:
                            if previous_tag == route[0]:
                                vehicle["vehicle"].set_target_speed(VEHICLE_SPEED)
                            elif reverse_previous_tag == route[0]:
                                vehicle["vehicle"].set_target_speed(-VEHICLE_SPEED)
                        elif not vehicle["arriving"] and route[1].split(".")[0] == vehicle["destination_node"].split(".")[0]:
                            print(f"Next node on route is destination node")
                            # if previous_tag == route[0]:
                            # get length of segment:
                            length = self.track_digraph.nodes.get(previous_tag)["length"]/2 + self.track_digraph.nodes.get(route[1])["length"]/2
                            
                            v0 = vehicle_speed#
                            a = vehicle["vehicle"].acceleration
                            braking_distance = v0**2/(2*a)
    
                            dist_until_braking = length - braking_distance * (1 - 0.3) # 30 percnet safetiy margin
                            time_until_braking = dist_until_braking / abs(v0) if abs(v0) > 0 else 0
    
                            print(f"Vehicle approaching destination, length until destination: {length}, current speed: {v0}, braking distance: {braking_distance}, time until braking: {time_until_braking}")
                            curr_timestamp = time.time_ns()/1e9
                            vehicle["braking_start_time"] = curr_timestamp + time_until_braking
                            vehicle["arriving"] = True
                        elif reverse_previous_tag == route[0]:
                            print(f"reversing")
                            if not vehicle["reversed_recently"]:
                                vehicle["vehicle"].set_target_speed(-vehicle_speed)
                                vehicle["reversed_recently"] = True
                        else:
                            vehicle["reversed_recently"] = False

                        if len(route) > 1 and (previous_tag == route[1]):
                            print(f"vehicle passed mid-point. previous tag: {previous_tag}, destination: {vehicle['destination_node']}")
                            # if len(route) > 1 and route[1].split(".")[0] == vehicle["destination_node"].split(".")[0]:
                            #     # if previous_tag == route[0]:
                            #     # get length of segment:
                            #     length = self.track_digraph.nodes.get(previous_tag)["length"]/2 + self.track_digraph.nodes.get(route[1])["length"]/2

                            #     v0 = vehicle_speed#
                            #     a = vehicle["vehicle"].acceleration
                            #     braking_distance = v0**2/(2*a)

                            #     dist_until_braking = length - braking_distance * (1 - 0.1) # 10 percnet safetiy margin
                            #     time_until_braking = dist_until_braking / abs(v0) if abs(v0) > 0 else 0

                            #     print(f"Vehicle approaching destination, length until destination: {length}, current speed: {v0}, braking distance: {braking_distance}, time until braking: {time_until_braking}")
                            #     curr_timestamp = time.time_ns()/1e9
                            #     vehicle["braking_start_time"] = curr_timestamp + time_until_braking
                            #     vehicle["arriving"] = True
                            vehicle["route"].pop(0)


                # check if 



###########################################
            # for vehicle in self.vehicles.values():
            #     # get vehicle last tag
            #     vehicle["last_tag"] = vehicle["vehicle"].last_tag
            #     last_tag = vehicle["last_tag"]
            #     # get neighbors of last tag-node
            #     if last_tag is None:
            #         continue

            #     if vehicle["route"] is None:
            #         vehicle["route"] = self._get_best_route(
            #             vehicle["vehicle"].position[0].get_key(),
            #             vehicle["destination_node"].split(".")[0],
            #             vehicle["vehicle"].position[1] + "_" + vehicle["vehicle"].position[2]
            #         )
            #         print("initial route: ", vehicle["route"])
            #         continue

            #     neighbors = list(self.track_digraph.neighbors(last_tag))
            #     if last_tag == vehicle["route"][0] and len(vehicle["route"]) > 1:
            #         vehicle["route"].pop(0)
                
            #     if vehicle["arriving"] and last_tag == vehicle["route"][0]:
            #         vehicle["vehicle"].set_target_speed(0)
            #         continue
            #     if len(vehicle["route"]) < 2:
            #         vehicle["arriving"] = True
            #         continue
                
            #     print(f"route: {vehicle['route']}, last tag: {last_tag}, neighbors: {neighbors}")
            #     # iterate over neighbors and check if one is first element of route
            #     if vehicle["route"][0] in neighbors:
            #         vehicle["vehicle"].set_target_speed(VEHICLE_SPEED)
            #         vehicle["route"].pop(0)
            #         break
            #     opposite_direction = last_tag.split(".")[0] + "." + last_tag.split(".")[1].split("_")[1] + "_" + last_tag.split(".")[1].split("_")[0]
            #     opposite_direction_neighbors = list(self.track_digraph.neighbors(opposite_direction))
            #     print("opposite direction: ", opposite_direction)
            #     print("opposite direction neighbors: ", opposite_direction_neighbors)
            #     if vehicle["route"][0] in opposite_direction_neighbors:
            #         vehicle["vehicle"].set_target_speed(-VEHICLE_SPEED)
            #         vehicle["route"].pop(0)
            #         break

            #     if vehicle["route"][0] not in neighbors and vehicle["route"][0] not in opposite_direction_neighbors:
            #         print(f"last tag neigbors: {list(neighbors)} not in first route element: {vehicle['route'][0]}, \n route: {vehicle['route']}")
            #         vehicle["route"] = self._get_best_route(
            #             vehicle["vehicle"].position[0].get_key(),
            #             vehicle["destination_node"].split(".")[0],
            #             vehicle["vehicle"].position[1] + "_" + vehicle["vehicle"].position[2]
            #         )


################################################

                # for neighbor in neighbors:
                #     # if so set target speet to 100 percent positve and remove first element of route
                #     if neighbor == vehicle["route"][0]:
                #         vehicle["vehicle"].set_target_speed(100)
                #         # vehicle["route"].pop(0)
                #         break
                #     # elif neighbor == vehicle["route"][1]:
                #     #     vehicle["vehicle"].set_target_speed(100)
                #     #     vehicle["route"].pop(0)
                #     #     vehicle["route"].pop(0)
                #     #     break
                #     # if not check opposite direction of the last tag is first element of route
                #     else:
                #         opposite_direction = last_tag.split(".")[0] + "." + last_tag.split(".")[1] + "_" + last_tag.split(".")[0]
                #         print("opposite direction: ", opposite_direction)
                #         if opposite_direction == vehicle["route"][0]:
                #             vehicle["vehicle"].set_target_speed(-100)
                #             # vehicle["route"].pop(0)
                #             break
                #     # if so set target speed to 100 percent negative and remove first element of route
                # # else: rerun route calculation and check again
                # print(f"last tag neigbors: {list(neighbors)} not in first route element: {vehicle['route'][0]}, \n route: {vehicle['route']}")
                # vehicle["route"] = self._get_best_route(
                #     vehicle["vehicle"].position[0].get_key(),
                #     vehicle["destination_node"].split(".")[0],
                #     vehicle["vehicle"].position[1] + "_" + vehicle["vehicle"].position[2]
                # )







                
                # if vehicle["vehicle"].position[0] is not vehicle["last_segment"]:

                #     for i in range(len(vehicle["route"]) -1, -1, -1):
                #         segment_end_ids = vehicle["route"][i - 1].split("_") + vehicle["route"][i].split("_")
                #         seen_segments = set()
                #         ends = {}
                #         # print("segment_end_ids: ", segment_end_ids)
                #         for segment_end_id in segment_end_ids:
                #             if segment_end_id.split(".")[0] in seen_segments:
                #                 duplicate_segment_id = segment_end_id.split(".")[0]
                #                 duplicate_segment_end_ids = [segment_end_id.split(".")[1], ends[segment_end_id.split(".")[0]]]
                #             if segment_end_id != "end":
                #                 ends[segment_end_id.split(".")[0]] = segment_end_id.split(".")[1]
                #             seen_segments.add(segment_end_id.split(".")[0])
                #             # print("seen_segments: ", seen_segments)

                #         # print(duplicate_segment_id)
                #         switch_segment: BaseSegment = self.track.segments[duplicate_segment_id]
                #         if isinstance(switch_segment, SegmentSwitch):
                #             if "c" in duplicate_segment_end_ids:
                #                 switch_segment.switch_setting = "c"
                #             elif "b" in duplicate_segment_end_ids:
                #                 switch_segment.switch_setting = "b"

                #     if vehicle["arriving"]:
                #         return vehicle["vehicle"].set_target_speed(0)
                #     v_t_speed = vehicle["vehicle"].target_speed
                #     v_pos = vehicle["vehicle"].position
                #     if v_pos[0].ends[v_pos[2]].get_end_id(True) == vehicle["route"][-1]:
                #         vehicle["arriving"] = True
                #     origin_end_id = v_pos[0].ends[v_pos[2 if v_t_speed < 0 else 1]].get_end_id(True)
                #     vehicle["route"] = self._get_best_route(
                #         origin_end_id,
                #         vehicle["destination_node"],
                #     )
                #     next_edge_id = v_pos[0].ends[v_pos[1 if v_t_speed < 0 else 2]].get_end_id(True)
                #     if next_edge_id not in set(vehicle["route"]):
                #         if v_t_speed > 0:
                #             vehicle["vehicle"].set_target_speed(-200)
                #         else:
                #             vehicle["vehicle"].set_target_speed(200)


                #     vehicle["last_segment"] = vehicle["vehicle"].position[0]

