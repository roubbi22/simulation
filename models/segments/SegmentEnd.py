from custom_types.EndVector import EndVector
from typing import TYPE_CHECKING

if TYPE_CHECKING: 
    from models.segments import BaseSegment
    from view import GraphicBaseSegment

class SegmentEnd():
    def __init__(self, vector: EndVector, parent_segment: "BaseSegment"):
        self.vector:EndVector  = EndVector(vector[0], vector[1], vector[2])
        self.connected_to: SegmentEnd = None
        self.graphic_representation: "GraphicBaseSegment" = None
        self.parent_segment: "BaseSegment" = parent_segment

    def get_end_id(self, include_connected_end:bool = False):
        for s_k, s_v in self.parent_segment.track.segments.items():
            if self.parent_segment is s_v:
                for e_k, e_v in s_v.ends.items():
                    if self is e_v:
                        own_id = f"{s_k}.{e_k}"
                        if not include_connected_end: return own_id
                        other_id = e_v.connected_to.get_end_id() if e_v.connected_to else "end"
                        return f"{own_id}_{other_id}" if other_id == "end" or (own_id < other_id) else f"{other_id}_{own_id}"
                    
        return "not found"