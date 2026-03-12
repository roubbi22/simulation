import sys
import math
from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsPathItem, QGraphicsEllipseItem
from PyQt6.QtGui import QPainterPath, QPen, QColor, QPainter
from PyQt6.QtCore import QRectF, Qt

class OpenSegmentEnd(QGraphicsEllipseItem):
    def __init__(self, parent_segment, end_coords):
        super().__init__(QRectF(-5, -5, 10, 10), parent_segment)
        self.parent_segment = parent_segment
        self.end_coords = end_coords
        self.setBrush(QColor("#003CFF"))
        self.setPen(QPen(Qt.GlobalColor.white, 2))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setZValue(10)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # open dialog to ask which kind of rail segment to add
            new_segment = SegmentStraight(100, (self.end_coords), 90)
            new_segment.setPos(self.end_coords[0], self.end_coords[1])
            # new_segment.setRotation(self.parent_segment)
            parent_scene = self.parent_segment.scene()
            if parent_scene:
                parent_scene.addItem(new_segment)

        return super().mousePressEvent(event)

# RailSegments

# Straight
class SegmentStraight(QGraphicsPathItem):

    def __init__(self, length, root_coords, root_hdg, connections={"a": None, "b": None}):
        super().__init__()
        self.length = length
        self.root_coords = root_coords
        self.root_hdg = root_hdg
        self.connections = connections

        path = QPainterPath()
        path.moveTo(0, 0)
        path.lineTo(0 + self.length, 0)
        self.setPath(path)
        self.setPen(QPen(QColor("#333333"), 4))

        self.a = (self.root_coords[0], self.root_coords[1], 0)
        self.b = (self.root_coords[0] + self.length, self.root_coords[1], 180)

        self.open_segment_ends = {
            "a": OpenSegmentEnd(self, self.a),
            "b": OpenSegmentEnd(self, self.b)
        }

        self.open_segment_ends["a"].setPos(0, 0) 
        self.open_segment_ends["b"].setPos(0 + self.length, 0) 


# Curve

# Switch


def main():
    app = QApplication(sys.argv)

    scene = QGraphicsScene()
    scene.setBackgroundBrush(QColor("#ffffff"))

    s1 = SegmentStraight(100, (0, 0), 90)
    # s1.setPos(1000, 200)
    scene.addItem(s1)

    print(s1.b)


    view = QGraphicsView(scene)
    view.setRenderHint(QPainter.RenderHint.Antialiasing)
    view.setWindowTitle("RailTrackViz")
    view.resize(1280, 720)

    view.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()