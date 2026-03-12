from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsPathItem, QGraphicsScene, QInputDialog, QInputDialog
from PyQt6.QtGui import QColor, QPainterPath, QPen
from PyQt6.QtCore import QRectF, Qt
from abc import abstractmethod
import numpy as np
import math

# from model import SegmentStraight

class ItemSegmentEnd(QGraphicsEllipseItem):
    def __init__(self, coords: list, parent_segment: GraphicBaseSegment, parent_segment_end, end_letter=None):
        super().__init__(QRectF(-6, -6, 12, 12), parent_segment)
        # print(f"[DEBUG] ItemSegmentEnd erzeugt für End: {parent_segment_end}")
        # print(f"end letter: {end_letter} at coords {coords}")
        self.coords = coords
        self.parent_segment = parent_segment
        self.parent_segment_end = parent_segment_end

        match end_letter:
            case "a":
                self.setBrush(QColor("#ffd000"))
            case "b":
                self.setBrush(QColor("#0044ff"))
            case "c":
                self.setBrush(QColor("#ff7b00"))

        self.setPen(QPen(QColor("white"), 2))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setZValue(10)

        self.direction_line = QGraphicsPathItem(self)
        path = QPainterPath()
        path.moveTo(0, 0)
        length = 16
        import math
        angle_rad = math.radians(self.coords[2])
        dx = length * math.sin(angle_rad)
        dy = -length * math.cos(angle_rad)
        path.lineTo(dx, dy)
        self.direction_line.setPath(path)
        self.direction_line.setPen(QPen(QColor("#ff0000"), 2))
        self.direction_line.setZValue(11)

        self.setPos(self.parent_segment_end.vector.x, self.parent_segment_end.vector.y)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            segment_types = ["Kurve links", "Kurve rechts", "Weiche links", "Weiche rechts", "Gerade"]
            selected_type, ok_type = QInputDialog.getItem(
                self.scene().views()[0],
                "Segmenttyp wählen",
                "Welcher Segmenttyp soll eingefügt werden?",
                segment_types,
                0,
                False
            )
            if ok_type:
                # End-Auswahl abhängig vom Typ
                if selected_type.startswith("Weiche"):
                    end_options = ["a", "b", "c"]
                else:
                    end_options = ["a", "b"]
                selected_end, ok_end = QInputDialog.getItem(
                    self.scene().views()[0],
                    "Segmentende wählen",
                    "Mit welchem Ende soll das Segment verbunden werden?",
                    end_options,
                    0,
                    False
                )
                if ok_end:
                    self.parent_segment.model.track.add_segment(
                        coords=self.coords,
                        segment_type=selected_type,
                        segment_end=self.parent_segment_end,
                        new_segment_starting_end=selected_end
                    )
                    if self.parent_segment_end.graphic_representation and self.parent_segment_end.graphic_representation.scene():
                        self.parent_segment_end.graphic_representation.scene().removeItem(self.parent_segment_end.graphic_representation)
                    self.parent_segment_end.graphic_representation = None
        return super().mousePressEvent(event)

    def update():
        pass


class GraphicBaseSegment(QGraphicsPathItem):
    def __init__(self, model_segment=None, scene=None):
        super().__init__()
        self.model = model_segment
        self.scene: QGraphicsScene = scene
        if self.model:
            self.update_from_model()
        if self.scene:
            self.scene.addItem(self)

    @abstractmethod
    def update_from_model(self):
        # print("updating item...")
        for key, end in self.model.ends.items():
            if end.connected_to is None and not end.graphic_representation:
                end.graphic_representation = ItemSegmentEnd(
                    [end.vector.x, end.vector.y, end.vector.angle],
                    self,
                    end,
                    key
                )
            elif end.graphic_representation and end.connected_to is not None:
                # print(f"removing item at end {end}")
                # print(f"removing segment end at {end.graphic_representation.pos()}")
                self.scene.removeItem(end.graphic_representation)
        pass

    @abstractmethod
    def removeSegment(self):
        self.model.track.remove_segment(self.model)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.removeSegment()
        return super().mousePressEvent(event)


class ItemSegmentStraight(GraphicBaseSegment):
    def __init__(self, model_segment, scene):
        super().__init__(model_segment, scene)

    def update_from_model(self):
        super().update_from_model()
        # print("updating segment item")
        vector_a = self.model.ends["a"].vector
        vector_b = self.model.ends["b"].vector

        path = QPainterPath()
        path.moveTo(vector_a.x, vector_a.y)
        path.lineTo(vector_b.x, vector_b.y)
        self.setPath(path)

        self.setPen(QPen(QColor("#333333"), 4))

        # for end in self.model.ends.values():
        #     if not end.connected_to:
        #         end.graphic_representation = ItemSegmentEnd(
        #             [end.vector.x, end.vector.y, end.vector.angle],
        #             self,
        #             end
        #         )
        #     elif end.graphic_representation:
        #         self.scene.removeItem(end.graphic_representation)
                

class ItemSegmentCurve(GraphicBaseSegment):
    def __init__(self, model_segment, scene):
        super().__init__(model_segment, scene)

    def update_from_model(self):
        super().update_from_model()
        path = QPainterPath()
        vector_a = self.model.ends["a"].vector
        vector_b = self.model.ends["b"].vector
        radius = float(self.model.radius) if isinstance(self.model.radius, (int, float, np.floating)) else float(self.model.radius[0])
        angle = self.model.angle

        radial_angle_a = np.radians(vector_a.angle + 90) if self.model.dir == "l" else np.radians(vector_a.angle - 90)

        center_x, center_y = (
            math.sin(radial_angle_a) * radius + vector_a.x,
            -math.cos(radial_angle_a) * radius + vector_a.y 
        )

        # radius = radius - 10

        rect = QRectF(center_x - radius, center_y - radius, 2 * radius, 2 * radius)
        
        start_angle = 180-vector_a.angle if self.model.dir == "l" else -vector_a.angle - angle
        span_angle = angle if isinstance(angle, (int, float)) else float(angle)

        start_x, start_y = (vector_a.x, vector_a.y) if self.model.dir == "l" else (vector_b.x, vector_b.y)
        path.moveTo(start_x, start_y)
        path.arcTo(rect, start_angle, span_angle)

        self.setPath(path)
        self.setPen(QPen(QColor("#333333"), 4))


class ItemSegmentSwitch(GraphicBaseSegment):
    def __init__(self, model_segment, scene):
        super().__init__(model_segment, scene)

    def update_from_model(self):
        super().update_from_model()
        path = QPainterPath()
        vector_a = self.model.ends["a"].vector
        vector_b = self.model.ends["b"].vector
        vector_c = self.model.ends["c"].vector
        radius = float(self.model.radius) if isinstance(self.model.radius, (int, float, np.floating)) else float(self.model.radius[0])
        angle = self.model.angle

        radial_angle_a = np.radians(vector_a.angle + 90) if self.model.dir == "l" else np.radians(vector_a.angle - 90)

        center_x, center_y = (
            math.sin(radial_angle_a) * radius + vector_a.x,
            -math.cos(radial_angle_a) * radius + vector_a.y 
        )

        # radius = radius - 10
        path = QPainterPath()
        path.moveTo(vector_a.x, vector_a.y)
        path.lineTo(vector_b.x, vector_b.y)
        self.setPath(path)

        self.setPen(QPen(QColor("#333333"), 4))

        rect = QRectF(center_x - radius, center_y - radius, 2 * radius, 2 * radius)
        
        start_angle = 180-vector_a.angle if self.model.dir == "l" else -vector_a.angle - angle
        span_angle = angle if isinstance(angle, (int, float)) else float(angle)

        start_x, start_y = (vector_a.x, vector_a.y) if self.model.dir == "l" else (vector_c.x, vector_c.y)
        path.moveTo(start_x, start_y)
        path.arcTo(rect, start_angle, span_angle)

        self.setPath(path)
        self.setPen(QPen(QColor("#333333"), 4))

        
        # radius = radius + 20
        
        # rect = QRectF(center_x - radius, center_y - radius, 2 * radius, 2 * radius)


        # start_x, start_y = (vector_a.x, vector_a.y)
        # path.moveTo(start_x, start_y)
        # path.arcTo(rect, start_angle, span_angle)

        # self.setPath(path)
        # self.setPen(QPen(QColor("#333333"), 4))


        # for end in self.model.ends.values():
        #     if not end.connected_to:
        #         end.graphic_representation = ItemSegmentEnd(
        #             [end.vector.x, end.vector.y, end.vector.angle],
        #             self,
        #             end
        #         )
        #     elif end.graphic_representation:
        #         self.scene.removeItem(end.graphic_representation)

# class ItemSegmentStraight(GraphicItem):
#     def __init__(
#             self,
#             model_segment,
#             scene: QGraphicsScene
#             ):
#         super().__init__()
#         # self.model = model_segment
#         # self.scene: QGraphicsScene = scene

#         vector_a = self.model.ends["a"].vector
#         vector_b = self.model.ends["b"].vector

#         # print("drawing segment:", self.model.ends["a"].vector)

#         path = QPainterPath()
#         path.moveTo(vector_a.x, vector_a.y)
#         path.lineTo(vector_b.x, vector_b.y)
#         self.setPath(path)

#         self.setPen(QPen(QColor("#333333"), 4))

#         # self.setPos(vector_a.x, vector_a.y)

#         for end in self.model.ends.values():
#             if not end.connected_to:
#                 # print(end.vector.x)
#                 end.graphic_representation = ItemSegmentEnd(
#                     [end.vector.x, end.vector.y, end.vector.angle],
#                     self
#                 )

#         if self.scene:
#             self.scene.addItem(self)

#     def update_from_model(self):
#         super().update_from_model()
#         vector_a = self.model.ends["a"].vector
#         vector_b = self.model.ends["b"].vector

#         path = QPainterPath()
#         path.moveTo(vector_a.x, vector_a.y)
#         path.lineTo(vector_b.x, vector_b.y)

#         self.setPath(path)