import networkx as nx

class Dijkstra:
    def find_path(self, graph: nx.Graph, start: str, end: str) -> list:
        """
        customly implemented Dijkstra algorithm to be extended to DijkstraRail 
        """ 
        print("start: ", start, "end: ", end)
        unvisited = {node: float('inf') for node in graph.nodes}
        unvisited[start] = 0
        visited = {}
        visited[start] = 0
        previous_nodes = {}
        while len(unvisited) > 0:
            current_node = min(unvisited, key=unvisited.get)
            if current_node == end:
                print("Dijkstra finished")
                visited[current_node] = unvisited[current_node]
                break
            for neighbor in graph.neighbors(current_node):
                if neighbor in visited:
                    continue
                accumulated_distance = unvisited[current_node] + graph[current_node][neighbor].get('length', 1)
                if accumulated_distance < unvisited[neighbor]:
                    unvisited[neighbor] = accumulated_distance
                    previous_nodes[neighbor] = current_node 
            visited[current_node] = unvisited[current_node]
            del unvisited[current_node]
        # print("previous_nodes[end]: ", previous_nodes[end])
        path = []
        current = end
        while current != start:
            path.append(current)
            current = previous_nodes[current]
        path.reverse()
        print(visited[end])
        return path
