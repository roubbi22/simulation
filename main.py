import sys
from PyQt6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QMainWindow, QMenuBar, QFileDialog, QDialog
from PyQt6.QtGui import QColor, QPainter, QAction
from PyQt6.QtCore import QTimer
from models.Track import Track
from models.VehicleController import VehicleController

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.timer = QTimer(self)
        self.setWindowTitle("RailTrackViz")
        self.showMaximized()

        # Szene und Track
        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(QColor("#E4E4E4"))
        self.track = Track(self.scene)
        self.vehicle_controller = VehicleController(self.track)

        origin_point = self.track.scene.addEllipse(-2, -2, 4, 4)
        origin_point.setBrush(QColor("#FF0000"))

        # View als zentrales Widget
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setCentralWidget(self.view)

        # Menüleiste
        menubar = QMenuBar(self)
        file_menu = menubar.addMenu("Datei")
        save_action = QAction("Speichern", self)
        save_action.triggered.connect(self.save_track)
        file_menu.addAction(save_action)

        save_as_action = QAction("Speichern unter...", self)
        save_as_action.triggered.connect(self.save_track_as)
        file_menu.addAction(save_as_action)

        file_open = QAction("Datei öffnen...", self)
        file_open.triggered.connect(self.open_file)
        file_menu.addAction(file_open)

        route_menu = menubar.addMenu("Simulation")

        self.setMenuBar(menubar)

        self.timer.timeout.connect(lambda: self.simulate(1/30))
        self.timer.start(int(1000/30))

    def simulate(self, delta_t):
        self.track.simulate(delta_t)

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Datei auswählen", "", "JSON Dateien (*.json);;Alle Dateien (*)")
        if file_path:
            if self.track.altered_since_save:
                from PyQt6.QtWidgets import QMessageBox
                reply = QMessageBox.question(
                    self,
                    "Änderungen nicht gespeichert",
                    "Es gibt ungespeicherte Änderungen. Trotzdem Datei öffnen und Änderungen verwerfen?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self.track.open_file(file_path)
            else:
                self.track.open_file(file_path)

    def save_track_as(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Speichern unter", "", "JSON Dateien (*.json);;Alle Dateien (*)")
        if file_path:
            self.track.store(file_path)

    def save_track(self):
        if self.track.file_path:
            self.track.store()
        else: 
            self.save_track_as()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()