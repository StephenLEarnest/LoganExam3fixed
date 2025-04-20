import sys
import os
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene
from circuit_parser import CircuitParser

class CircuitViewer(QGraphicsView):
    def __init__(self, file_path):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setSceneRect(0, 0, 800, 600)

        parser = CircuitParser(self.scene)
        parser.parse_file(file_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, "circuit.txt")
    viewer = CircuitViewer(file_path)
    viewer.setWindowTitle("RLC Circuit Viewer")
    viewer.resize(800, 600)
    viewer.show()
    sys.exit(app.exec_())

