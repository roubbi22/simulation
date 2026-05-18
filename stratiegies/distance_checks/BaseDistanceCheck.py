import networkx as nx
from typing import Tuple
from abc import ABC, abstractmethod

class BaseDistanceCheck(ABC):
    def __init__(self):
        super().__init__()
        self = self

    @abstractmethod
    def check_distance(self, graph: nx.DiGraph, start_node: str, req_dist_1: float, req_dist_2: float = None) -> Tuple[list, float]:
        pass