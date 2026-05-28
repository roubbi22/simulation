from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsPathItem, QGraphicsScene, QGraphicsView, QInputDialog, QInputDialog, QMenu
from PyQt6.QtGui import QColor, QPainterPath, QPen
from PyQt6.QtCore import QRectF, Qt
from abc import abstractmethod
import numpy as np
import math

from custom_types import EndVector
from models.segments import BaseSegment, SegmentEnd

class ItemSegmentEnd(QGraphicsEllipseItem):
    def __init__(self, coords: list, parent_segment: GraphicBaseSegment, parent_segment_end, end_letter=None):
        super().__init__(QRectF(-6, -6, 12, 12), parent_segment)
        self.coords = coords
        self.parent_segment: GraphicBaseSegment = parent_segment
        self.parent_segment_end: SegmentEnd = parent_segment_end

        match end_letter:
            case "a":
                self.setBrush(QColor("#dab200"))
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
        if self.scene():
            self.scene().update()

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
    def __init__(self, scene, model_segment=None,):
        super().__init__()
        self.model: BaseSegment = model_segment
        self.scene: QGraphicsScene = scene
        self.display_color = QColor("#333333")
        self.original_color: QColor = QColor("#333333")
        self.marker_items: list[QGraphicsPathItem] = []
        if self.model:
            self.update_from_model()
        if self.scene:
            self.scene.addItem(self)
        self.setAcceptHoverEvents(True)

    def _set_origin_destination(self, is_origin: bool | None, is_destination: bool | None):
        if is_origin is not None:
            self.model.is_allowed_origin = (100, 100) if is_origin else None
        if is_destination is not None:
            self.model.is_allowed_destination = (100, 100) if is_destination else None
        if self.model:
            self.update_from_model()

    def _clear_marker_items(self):
        for marker_item in self.marker_items:
            if marker_item.scene():
                marker_item.scene().removeItem(marker_item)
        self.marker_items.clear()

    def _add_status_marker(self, is_origin: bool, is_destination: bool):
        self._clear_marker_items()

        if not is_origin and not is_destination:
            return

        path = self.path()
        if path.isEmpty():
            return



        if is_origin:
            origin_marker_path = QPainterPath()
            origin_marker_path.addEllipse(QRectF(-7, -7, 14, 14))
            origin_marker_path.addEllipse(QRectF(-3, -3, 6, 6))
    
            origin_marker_item = QGraphicsPathItem(self)
            origin_marker_item.setPath(origin_marker_path)
    
            marker_point = path.pointAtPercent(0.5)
            origin_marker_item.setPos(marker_point.x(), marker_point.y())
            origin_marker_item.setRotation(path.angleAtPercent(0.5) - 90)
            origin_marker_item.setZValue(self.zValue() + 2)
            origin_marker_item.setBrush(QColor("black"))
            origin_marker_item.setPen(QPen(QColor("black"), 1))

            self.marker_items.append(origin_marker_item)
        if is_destination:
            destination_marker_path = QPainterPath()
            destination_marker_path.addEllipse(QRectF(-10, -10, 20, 20))
            destination_marker_path.addEllipse(QRectF(-7, -7, 14, 14))
    
            destination_marker_item = QGraphicsPathItem(self)
            destination_marker_item.setPath(destination_marker_path)
    
            destmarker_point = path.pointAtPercent(0.5)
            destination_marker_item.setPos(destmarker_point.x(), destmarker_point.y())
            destination_marker_item.setRotation(path.angleAtPercent(0.5) - 90)
            destination_marker_item.setZValue(self.zValue() + 2)
            destination_marker_item.setBrush(QColor("white"))
            destination_marker_item.setPen(QPen(QColor("black"), 1))

            self.marker_items.append(destination_marker_item)
    
    @abstractmethod
    def update_from_model(self):
        for key, end in self.model.ends.items():
            if end.connected_to is None and not end.graphic_representation:
                end.graphic_representation = ItemSegmentEnd(
                    [end.vector.x, end.vector.y, end.vector.angle],
                    self,
                    end,
                    key
                )
            elif end.graphic_representation and end.connected_to is not None:
                if end.graphic_representation and end.graphic_representation.scene() == self.scene:
                    self.scene.removeItem(end.graphic_representation)
        pass

    @abstractmethod
    def removeSegment(self):
        self.model.track.remove_segment(self.model)

    def hoverEnterEvent(self, event):
        self.display_color = QColor("#3700FF")
        self.update_from_model()
        return super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.display_color = self.original_color
        self.update_from_model()
        return super().hoverLeaveEvent(event)

    @abstractmethod
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            menu = QMenu()
            menu.addAction("Segment entfernen", lambda: self.removeSegment())
            if self.model.is_allowed_origin:
                menu.addAction("Startpunkt entfernen", lambda: self._set_origin_destination(False, None))
            else:
                menu.addAction("Startpunkt setzen", lambda: self._set_origin_destination(True, None))
            if self.model.is_allowed_destination:
                menu.addAction("Zielpunkt entfernen", lambda: self._set_origin_destination(None, False))
            else:
                menu.addAction("Zielpunkt setzen", lambda: self._set_origin_destination(None, True))
            menu.addAction("Fahrzeug positionieren", lambda :self._add_vehicle())
            menu.exec(event.screenPos())
            # rerender
            if self.scene:
                self.scene.update()
        return super().mousePressEvent(event)
    
    def _add_vehicle(self):
        from vehicle import Vehicle
        vehicle = Vehicle(scene=self.scene, segment=self.model, from_end="a", to_end="b", percentage=0.5)
        self.model.track.add_vehicle(vehicle)


class ItemSegmentStraight(GraphicBaseSegment):
    def __init__(self, model_segment, scene):
        super().__init__(scene, model_segment)

    def update_from_model(self):
        super().update_from_model()
        vector_a = self.model.ends["a"].vector
        vector_b = self.model.ends["b"].vector

        path = QPainterPath()
        path.moveTo(vector_a.x, vector_a.y)
        path.lineTo(vector_b.x, vector_b.y)
        self.setPath(path)
        if not self.model.annotated:
            self.setPen(QPen(self.display_color, 4))
        else:
            self.setPen(QPen(QColor('#33ff00'), 4))
        self._add_status_marker(bool(self.model.is_allowed_origin), bool(self.model.is_allowed_destination))
        if self.scene:
            self.scene.update()

class ItemSegmentCurve(GraphicBaseSegment):
    def __init__(self, model_segment, scene):
        super().__init__(scene, model_segment)

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
        if not self.model.annotated:
            self.setPen(QPen(self.display_color, 4))
        else:
            self.setPen(QPen(QColor('#33ff00'), 4))
        self._add_status_marker(bool(self.model.is_allowed_origin), bool(self.model.is_allowed_destination))
        if self.scene:
            self.scene.update()

class ItemSegmentSwitch(GraphicBaseSegment):
    def __init__(self, model_segment, scene):
        super().__init__(scene, model_segment)

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

        straight_offset = 75 if self.model.switch_setting == "c" else 0
        curve_offset = 10 if self.model.switch_setting == "b" else 0
        if self.model.dir == "r": curve_offset = - curve_offset

        path = QPainterPath()
        path.moveTo(
            vector_a.x + (-math.sin(np.radians(vector_a.angle)) * straight_offset),
            vector_a.y + (math.cos(np.radians(vector_a.angle)) * straight_offset)
        )
        path.lineTo(vector_b.x, vector_b.y)
        self.setPath(path)
        if not self.model.annotated:
            self.setPen(QPen(self.display_color, 4))
        else:
            self.setPen(QPen(QColor('#33ff00'), 4))
        self._add_status_marker(bool(self.model.is_allowed_origin), bool(self.model.is_allowed_destination))
        if self.scene:
            self.scene.update()

        rect = QRectF(center_x - radius, center_y - radius, 2 * radius, 2 * radius)
        
        start_angle = 180-vector_a.angle if self.model.dir == "l" else -vector_a.angle
        span_angle = angle if isinstance(angle, (int, float)) else float(angle)

        start_x, start_y = (vector_a.x, vector_a.y)

        start_coords = EndVector(
            start_x, start_y, 270
        )

        rotation_center = (
            start_x + (math.cos(np.radians(vector_a.angle)) * self.model.radius) if self.model.dir == "l" else start_x + (-math.cos(np.radians(vector_a.angle)) * self.model.radius),
            start_y + (math.sin(np.radians(vector_a.angle)) * self.model.radius) if self.model.dir == "l" else start_y + (-math.sin(np.radians(vector_a.angle)) * self.model.radius),
        )

        start_coords.rotate(rotation_center, - curve_offset)

        directed_span_angle = span_angle if self.model.dir == "l" else -span_angle

        path.moveTo(start_coords.x, start_coords.y)
        path.arcTo(rect, start_angle + curve_offset, directed_span_angle - curve_offset)
        self.setPath(path)
        if not self.model.annotated:
            self.setPen(QPen(self.display_color, 4))
        else:
            self.setPen(QPen(QColor('#33ff00'), 4))
        self._add_status_marker(bool(self.model.is_allowed_origin), bool(self.model.is_allowed_destination))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            menu = QMenu()
            menu.addAction("Segment entfernen", lambda: self.removeSegment())
            if self.model.is_allowed_origin:
                menu.addAction("Startpunkt entfernen", lambda: self._set_origin_destination(False, None))
            else:
                menu.addAction("Startpunkt setzen", lambda: self._set_origin_destination(True, None))
            if self.model.is_allowed_destination:
                menu.addAction("Zielpunkt entfernen", lambda: self._set_origin_destination(None, False))
            else:
                menu.addAction("Zielpunkt setzen", lambda: self._set_origin_destination(None, True))
            menu.addAction("Fahrzeug positionieren", lambda :self._add_vehicle())
            menu.addAction("Weiche umstellen", self.toggle_switch)
            menu.exec(event.screenPos())
            # rerender 
            if self.scene:
                self.scene.update()
        return super().mousePressEvent(event)

    def toggle_switch(self):
        self.model.toggle_switch_setting()

class ItemVehicle(QGraphicsPathItem):
    def __init__(self, scene, model_vehicle,):
        from vehicle import Vehicle
        super().__init__()
        self.model_vehicle: Vehicle = model_vehicle
        self.scene: QGraphicsScene = scene
        self.display_color: QColor = QColor("#333333")
        self.original_color: QColor = QColor("#333333")
        self.wagon_items: list[QGraphicsPathItem] = []
        self.direction_line = QGraphicsPathItem(self)
        if self.model_vehicle:
            self.update_from_model()
        if self.scene:
            self.scene.addItem(self)
        self.setAcceptHoverEvents(True)


    def _vehicle_local_position(self, coords: EndVector) -> tuple[float, float]:
        vehicle_coords = self.model_vehicle.coords
        delta_x = coords.x - vehicle_coords.x
        delta_y = coords.y - vehicle_coords.y
        angle_rad = math.radians(-vehicle_coords.angle)
        local_x = delta_x * math.cos(angle_rad) - delta_y * math.sin(angle_rad)
        local_y = delta_x * math.sin(angle_rad) + delta_y * math.cos(angle_rad)
        return local_x, local_y


    def _clear_wagon_items(self):
        for wagon_item in self.wagon_items:
            if wagon_item.scene():
                wagon_item.scene().removeItem(wagon_item)
        self.wagon_items.clear()


    def update_from_model(self):
        self._clear_wagon_items()

        path = QPainterPath()
        rect = QRectF(-10, -self.model_vehicle.locomotive_length/2, 20, self.model_vehicle.locomotive_length)
        path.addRect(rect)

        self.setPath(path)
        self.setPen(QPen(QColor("#123456"), 4))
        self.setBrush(QColor("#fdfeff"))
        self.setZValue(12) 

        dir_path = QPainterPath()
        dir_path.moveTo(0, -15)
        dir_path.lineTo(0, -30)
        self.direction_line.setPath(dir_path)
        self.direction_line.setPen(QPen(QColor("#0000ff"), 2))
        self.direction_line.setZValue(12)
        self.setPos(self.model_vehicle.coords.x, self.model_vehicle.coords.y)
        self.setRotation(self.model_vehicle.coords.angle)

        for wagon in self.model_vehicle.wagons_front + self.model_vehicle.wagons_rear:
            wagon_length, wagon_coords = wagon
            if wagon_coords is None:
                continue

            wagon_path = QPainterPath()
            wagon_path.addRect(QRectF(-10, -wagon_length / 2, 20, wagon_length))

            wagon_item = QGraphicsPathItem(self)
            wagon_item.setPath(wagon_path)
            wagon_item.setPen(QPen(QColor("#123456"), 4))
            wagon_item.setBrush(QColor("#fdfeff"))
            wagon_item.setZValue(12.1)

            local_x, local_y = self._vehicle_local_position(wagon_coords)
            wagon_item.setPos(local_x, local_y)
            wagon_item.setRotation(wagon_coords.angle - self.model_vehicle.coords.angle)
            self.wagon_items.append(wagon_item)

        if self.scene:
            self.scene.update()