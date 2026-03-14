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