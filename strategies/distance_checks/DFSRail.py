from abc import ABC
from typing import Tuple
import networkx as nx

from strategies.distance_checks.BaseDistanceCheck import BaseDistanceCheck

class DFSRail(BaseDistanceCheck):
    def __init__(self):
        super().__init__()

    def _build_dfs_path(self, visited: set, last: str) -> list:
        path = []
        curr = last
    
        parent_map = {node: (dist, prev) for dist, node, prev, visited_segments in visited}
    
        while curr:
            dist, prev = parent_map[curr]
            path.append((curr))
            curr = prev

        backtrack_path = []
        for node in path:
            if node != path[-1]: # do not add opposite direction for first node because it must not be the direct opposite but the opposite diverging branch of switch
                segment, direction = str(node).split(".")
                from_end, to_end = str(direction).split("_")
                backtrack_path.append(f"{segment}.{to_end}_{from_end}")
    
        path.reverse()

        return [*path, *backtrack_path]

    def check_distance(self, graph: nx.DiGraph, start_node: str, req_dist_1: float, req_dist_2: float = None) -> Tuple[list, float]:
        """
        depth first search algorithm, adapted for rail-based scenarios

            params:
            - graph: networkx DiGraph representation of the rail system
            - start_node: id of the start node
            - req_dist_1: required distance to the reference point (e.g. wagons behind the locomotive + part of the locomotive behind the reference point)
            - req_dist_2: optional: requiered distance from the reference point (e.g. for the part of the locomotive in front of the reference point + pushed wagons)

            returns:
            tuple, containing:
                [0]: list of all nodes to the first possible return node
                [1]: distance to the first possible return node (e.g. to use for virtual saw edges in pathfinding algorithms)

        """
        visited = set()
        unvisited = [(0, start_node, None, (start_node.split(".")[0],))]

        while unvisited:
            dist, curr, prev, visited_segments = unvisited.pop()
            state = (dist, curr, prev, visited_segments)
            if state in visited:
                continue
            visited.add(state)

            if dist >= req_dist_1:
                if not req_dist_2 or req_dist_2 == 0 or (self.check_distance(graph, curr, req_dist_2)[1] > 0):
                    return (self._build_dfs_path(visited, curr), dist)

            for next_neighbor in graph.neighbors(curr):
                neighbor_segment = str(next_neighbor).split(".")[0]
                if neighbor_segment not in visited_segments:  # as neighbor-node of virtual saw edge is of the same segment, this also prohibits using branch-branch edges for dfs           
                    new_segments = visited_segments + (neighbor_segment,)

                    unvisited.append(
                        (
                            dist + graph.nodes.get(curr)["length"]/2 + graph.nodes.get(next_neighbor)["length"]/2,
                            next_neighbor,
                            curr,
                            new_segments
                        )
                    )
        return ([], 0.0)