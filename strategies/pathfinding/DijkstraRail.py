import networkx as nx
from strategies.distance_checks import BaseDistanceCheck, DFSRail

class DijkstraRail:
    def __init__(self):
        self.DistanceCheck = DFSRail()

    def _invert_segment_dir(self, forward_dir: str) -> str:
        from_end, to_end = forward_dir.split("_")
        return f"{to_end}_{from_end}"

    def find_path(self, graph: nx.DiGraph, start_segment: str, end_segment: str, t_lr: float, t_lf: float = 0, shunting_overrun_penalty: float = 0, initial_orientation: str = "a_b") -> list:
        """
        customly implemented Dijkstra algorithm to be extended to DijkstraRail 
        """ 
        unvisited = {}
        for node in graph.nodes:
            unvisited[(node, 0)] = float("inf")
            unvisited[(node, 1)] = float("inf")

        visited = set()
        previous_states = {}
        shunting_overrun_nodes = {}

        unvisited[(f"{start_segment}{initial_orientation}"), 0] = 0
        unvisited[(f"{start_segment}{self._invert_segment_dir(initial_orientation)}"), 1] = 0

        last_state = None

        while len(unvisited) > 0:
            current_state = min(unvisited, key=unvisited.get)
            current_node, current_orientation = current_state

            if unvisited[current_state] == float("inf"):
                break

            if str(current_node).startswith(end_segment):
                print("Dijkstra finished")
                last_state = current_state
                break

            current_dist = unvisited[current_state]
            visited.add(current_state)

            for neighbor in graph.neighbors(current_node):
                edge_data = graph.get_edge_data(current_node, neighbor)
                is_virtual_saw = edge_data.get("virtual_saw", False)

                if is_virtual_saw:
                    neighbor_orientation = 1 - current_orientation
                else: neighbor_orientation = current_orientation

                neighbor_state = (neighbor, neighbor_orientation)

                if neighbor_state in visited:
                    continue
                if is_virtual_saw:
                    if current_orientation == 0:
                        shunting_overrun = self.DistanceCheck.check_distance(graph, current_node, t_lr, t_lf)
                    else:
                        shunting_overrun = self.DistanceCheck.check_distance(graph, current_node, t_lf, t_lr)
                    if not shunting_overrun[1] > 0:
                        continue
                    accumulated_distance = unvisited[current_state] + shunting_overrun[1] + shunting_overrun_penalty
                    shunting_overrun_nodes[current_node] = [*shunting_overrun[0], neighbor]
                else:
                    req_dist_front = t_lf if current_orientation == 0 else t_lr
                    if self.DistanceCheck.check_distance(graph, neighbor, req_dist_front)[1] == 0:
                        continue
                    else: accumulated_distance = current_dist + graph.nodes.get(current_node)["length"]/2 + graph.nodes.get(neighbor)["length"]/2

                if neighbor_state in unvisited and accumulated_distance < unvisited[neighbor_state]:
                    unvisited[neighbor_state] = accumulated_distance
                    previous_states[neighbor_state] = current_state

            del unvisited[current_state]

        state_path = []
        current = last_state

        while current is not None:
            state_path.append(current)
            current = previous_states.get(current, None)

        path = [state[0] for state in state_path]
        path.reverse()

        if len(path) > 1:
            for overrun_origin in shunting_overrun_nodes.keys():
                # if a shunting overrun was used (path[i] is orgin of overrun and path[i+1] is destination of overrun) add the overrun nodes to the path
                for i in range(len(path)-1):
                    if path[i] == overrun_origin and path[i+1] == shunting_overrun_nodes[overrun_origin][-1]:
                        overrun_nodes = list(shunting_overrun_nodes[overrun_origin])
                        overrun_nodes = overrun_nodes[1:-1]
                        overrun_nodes.reverse()
                        for overrun_node in overrun_nodes:
                            path.insert(i+1, overrun_node)
        return path
