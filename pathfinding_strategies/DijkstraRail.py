import networkx as nx
from strategies.distance_checks import BaseDistanceCheck, DFSRail

class DijkstraRail:
    def __init__(self):
        self.DistanceCheck = DFSRail()

    def find_path(self, graph: nx.DiGraph, start_segment: str, end_segment: str, t_lr: float, t_lf: float = 0, shunting_overrun_penalty: float = 0) -> list:
        """
        customly implemented Dijkstra algorithm to be extended to DijkstraRail 
        """ 
        unvisited = {node: float('inf') for node in graph.nodes}
        visited = {}
        start_nodes = [n for n in graph.nodes if str(n).startswith(start_segment)]
        shunting_overrun_nodes = {}
        for node in start_nodes:
            unvisited[node] = 0
            visited[node] = 0

        visited = {}
        previous_nodes = {}
        last_node: str = ""
        while len(unvisited) > 0:
            current_node = min(unvisited, key=unvisited.get)
            if str(current_node).startswith(end_segment):
                print("Dijkstra finished")
                visited[current_node] = unvisited[current_node]
                last_node = current_node
                break
            for neighbor in graph.neighbors(current_node):
                if neighbor in visited:
                    continue
                if graph.get_edge_data(current_node, neighbor)["virtual_saw"]:
                    shunting_overrun = self.DistanceCheck.check_distance(graph, current_node, t_lr, t_lf)
                    if not shunting_overrun[1] > 0:
                        continue
                    accumulated_distance = unvisited[current_node] + shunting_overrun[1] + shunting_overrun_penalty
                    shunting_overrun_nodes[current_node] = [*shunting_overrun[0], neighbor]
                elif self.DistanceCheck.check_distance(graph, neighbor, t_lf)[1] == 0:
                    continue
                else:
                    accumulated_distance = unvisited[current_node] + graph.nodes.get(current_node)["length"]/2 + graph.nodes.get(neighbor)["length"]/2
                if accumulated_distance < unvisited[neighbor]:
                    unvisited[neighbor] = accumulated_distance
                    previous_nodes[neighbor] = current_node 
            visited[current_node] = unvisited[current_node]
            del unvisited[current_node]

        path = []
        current = last_node
        print(previous_nodes)
        if current in previous_nodes:
            while not str(current).startswith(start_segment):
                path.append(current)
                current = previous_nodes[current]
        else: return []
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
                    # if overruns 
        return path
