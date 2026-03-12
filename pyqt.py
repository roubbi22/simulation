# from PyQt6.QtWidgets import QGraphicsItem, QGraphicsScene, QGraphicsView, QApplication
# from PyQt6.QtGui import QPainter, QPen, QColor
# from PyQt6.QtCore import QRectF, QLineF
# import sys

# # class BaseRailSegment():
# #     """
# #     Base class of rail segments
# #     attributes:
# #     nodes: obj[]
# #     edges: obj[]
# #     """
# #     # def __init__(self, )

# #     def paint():

# class GleisSegment(QGraphicsItem):
#     def __init__(self, laenge=200):
#         super().__init__()
#         self.laenge = laenge
#         self.spurweite = 20
#         self.schwellen_abstand = 15

#     def boundingRect(self):
#         # Definiert den Bereich, den das Gleis einnimmt (für das Rendering wichtig)
#         return QRectF(0, -15, self.laenge, 30)

#     def paint(self, painter, option, widget):
#         # 1. Schwellen zeichnen
#         painter.setPen(QPen(QColor("#5D4037"), 4)) # Dunkelbraun
#         for x in range(0, self.laenge, self.schwellen_abstand):
#             painter.drawLine(x, -12, x, 12)

#         # 2. Schienenprofile zeichnen (Stahl-Optik)
#         stahl_pen = QPen(QColor("#9E9E9E"), 3)
#         painter.setPen(stahl_pen)
#         # Nutze // statt /
#         painter.drawLine(0, int(-self.spurweite // 2), self.laenge, int(-self.spurweite // 2))
#         painter.drawLine(0, int(self.spurweite // 2), self.laenge, int(self.spurweite // 2))

# class GenericSegment(QGraphicsItem):

#     def paint(self, painter, option, widget):
#         # painter.drawLine(10, 10, 20, 20)

#         rectangle = QRectF(0.0, 0.0, 100, 100.0)
#         startAngle = 30 * 16
#         spanAngle = 120 * 16
#         # painter = QPainter(self)
#         painter.drawArc(rectangle, 0 * 16, 30 * 16)


# # --- Standard PyQt Setup ---
# app = QApplication(sys.argv)
# scene = QGraphicsScene()
# view = QGraphicsView(scene)
# view.setRenderHint(QPainter.RenderHint.Antialiasing) # Macht Linien glatt

# # Gleis platzieren
# gleis = GleisSegment(300)
# generic = GenericSegment()
# # scene.drawBackground()
# scene.addItem(generic)

# view.resize(500, 200)
# # view.drawBackground()
# view.show()
# sys.exit(app.exec())

# ---------------------------------------------

# from PyQt6.QtWidgets import QApplication, QPushButton, QWidget, QVBoxLayout
# import sys

# app = QApplication(sys.argv)
# window = QWidget()
# layout = QVBoxLayout()

# button = QPushButton("Klick mich!")
# button.clicked.connect(lambda: print("Hallo Welt!")) # Signal -> Slot

# layout.addWidget(button)
# window.setLayout(layout)
# window.show()

# sys.exit(app.exec())

# ---------------------------------------------

# from PyQt6.QtWidgets import QGraphicsItem, QGraphicsScene, QGraphicsView, QApplication
# from PyQt6.QtGui import QPainter, QPen, QColor, QPainterPath
# from PyQt6.QtCore import QRectF, QLineF
# import sys
# import math

# # rail-segment types:
# # st: straight
# # cl: curve-left
# # cr: curve-right
# # sl: switch-left
# # sr: switch-right

# class SegmentStraight(QGraphicsItem):
#     def __init__(self, root_coords, root_heading, length=200):
#         super().__init__()
#         self.root_coords = root_coords
#         self.root_heading_rad = math.radians(root_heading)
#         self.length = length

#     def paint(self, painter, option, widget):

#         painter.setPen(QColor("#000"))

        
#         painter.drawLine(
#             self.root_coords[0],
#             self.root_coords[1],
#             self.root_coords[0] + int(math.sin(self.root_heading_rad) * self.length),
#             self.root_coords[1] - int(math.cos(self.root_heading_rad) * self.length)
#             )
        
# class SegmentCurve(QGraphicsItem):
#     def __init__(self, root_coords, root_heading, direction, radius, angle = 30, length=200):
#         super().__init__()
#         self.root_coords = root_coords
#         self.root_heading_deg = root_heading
#         self.root_heading_rad = math.radians(root_heading)
#         self.radius = radius
#         self.length = length
#         self.angle = angle

#     def paint(self, painter, option, widget):

#         painter.setPen(QColor("#000"))

#         rect = QRectF(
#             self.root_coords[0]-self.radius,
#             self.root_coords[1],
#             self.radius*2,
#             self.radius*2
#         )
#         path=QPainterPath()
#         path.arcMoveTo(rect, 90)
#         path.arcTo(rect, 90, -30)
        
#         painter.drawPath(path)
#         painter.drawLine(
#             self.root_coords[0],
#             self.root_coords[1],
#             self.root_coords[0],
#             self.root_coords[1] + self.radius,
#         )
#         # return path
        
# app = QApplication(sys.argv) 
# scene = QGraphicsScene()

# scene.setBackgroundBrush(QColor("#ffffff"))

# s1 = SegmentStraight((0, 0), 90, 100)
# s2 = SegmentStraight((-250, -150), 135)
# s3 = SegmentStraight((20, 20), 10)
# s4 = SegmentStraight((20, 20), 15)

# cr1 = SegmentCurve((100, 0), 45, "r", 100, 30)
# cr1 = SegmentCurve((100, 0), 45, "r", 100, 30)
# cr2 = SegmentCurve((0, 0), 0, "r", 50, 30)
# cr3 = SegmentCurve((0, 0), 0, "r", 50, 30)
# cr4 = SegmentCurve((0, 0), 0, "r", 50, 30)
# # cr1.setRotation(-45)
# # cr2.setRotation(45)
# # cr3.setRotation(135)
# # cr4.setRotation(225)

# scene.addItem(s1)
# # scene.addItem(s2)
# # scene.addItem(s3)
# # scene.addItem(s4)
# scene.addItem(cr1)
# # scene.addItem(cr2)
# # scene.addItem(cr3)
# # scene.addItem(cr4)


# view = QGraphicsView(scene)

# view.setFixedSize(1000, 600)



# view.show()
# sys.exit(app.exec())


# ---------------------------------------------

import sys
import math
from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsPathItem, QGraphicsEllipseItem
from PyQt6.QtGui import QPainterPath, QPen, QColor, QPainter
from PyQt6.QtCore import QRectF, Qt

# --- UNSERE LOGIK-KLASSEN ---

class ConnectorItem(QGraphicsEllipseItem):
    def __init__(self, parent_gleis):
        super().__init__(QRectF(-6, -6, 12, 12), parent_gleis)
        self.parent_gleis = parent_gleis
        self.setBrush(QColor("red"))
        self.setPen(QPen(Qt.GlobalColor.white, 2))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setZValue(10) # Immer oben liegen

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Hier bauen wir interaktiv ein neues Teil an
            neues_gleis = GleisSegment(radius=200, winkel=30, parent=self.parent_gleis)
            neues_gleis.setPos(self.parent_gleis.end_x, self.parent_gleis.end_y)
            neues_gleis.setRotation(self.parent_gleis.winkel)
            self.setVisible(False) # Alten Connector verstecken
        super().mousePressEvent(event)

class GleisSegment(QGraphicsPathItem):
    def __init__(self, radius, winkel, parent=None):
        super().__init__(parent)
        self.radius = radius
        self.winkel = winkel
        
        path = QPainterPath()
        # Wichtig: Startet im Ursprung (0,0)
        rect = QRectF(-radius, 0, radius * 2, radius * 2)
        path.arcMoveTo(rect, 90)
        path.arcTo(rect, 90, -winkel)
        self.setPath(path)
        self.setPen(QPen(QColor("#333333"), 4))
        
        # Endpunkt berechnen
        rad = math.radians(90 - self.winkel)
        self.end_x = self.radius * math.cos(rad)
        self.end_y = self.radius - (self.radius * math.sin(rad))
        
        # Connector hinzufügen
        self.connector = ConnectorItem(self)
        self.connector.setPos(self.end_x, self.end_y)

# --- DIE ANZEIGE-STRUKTUR ---

def main():
    app = QApplication(sys.argv)

    # 1. Szene erstellen (Die Welt)
    scene = QGraphicsScene()
    scene.setBackgroundBrush(QColor("#e0e0e0")) # Hellgrauer Hintergrund

    # 2. Das erste Gleisstück platzieren (Startpunkt)
    start_gleis = GleisSegment(radius=200, winkel=30)
    start_gleis.setPos(100, 300) # Irgendwo in der Mitte starten
    scene.addItem(start_gleis)

    # 3. View erstellen (Das Guckloch)
    view = QGraphicsView(scene)
    view.setRenderHint(QPainter.RenderHint.Antialiasing) # Wichtig für glatte Kurven!
    view.setWindowTitle("Interaktiver Gleisplan Editor")
    view.resize(800, 600)
    
    view.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()