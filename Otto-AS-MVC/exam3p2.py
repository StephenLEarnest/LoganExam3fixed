import sys
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QMainWindow
from circuit_parser import CircuitParser
from circuit_elements import Resistor, Capacitor, Inductor, VoltageSource

class CircuitViewer(QMainWindow):
    def __init__(self, nodes, elements):
        super().__init__()
        self.setWindowTitle("RLC Circuit Viewer")
        self.view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        self.setCentralWidget(self.view)
        self.nodes = nodes
        self.elements = elements
        self.draw_elements()

    def draw_elements(self):
        for elem in self.elements:
            start = self.nodes[elem['from']]
            end = self.nodes[elem['to']]
            element_type = elem['type']

            if element_type == 'resistor':
                item = Resistor(start, end)
            elif element_type == 'capacitor':
                item = Capacitor(start, end)
            elif element_type == 'inductor':
                item = Inductor(start, end)
            elif element_type == 'voltagesource':
                item = VoltageSource(start, end)
            else:
                continue

            self.scene.addItem(item)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    parser = CircuitParser("circuit.txt")
    nodes, elements = parser.parse()
    viewer = CircuitViewer(nodes, elements)
    viewer.resize(600, 600)
    viewer.show()
    sys.exit(app.exec_())
