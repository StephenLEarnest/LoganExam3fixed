import sys
import xml.etree.ElementTree as ET
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QMainWindow, QGraphicsItem
from PyQt5.QtGui import QPainter, QPen, QBrush
from PyQt5.QtCore import Qt, QRectF, QPointF
from math import sqrt

# Node graphics item
class NodeItem(QGraphicsItem):
    def __init__(self, node_id, x, y):
        super().__init__()
        self.node_id = node_id
        self.setPos(x, y)
        self.radius = 5
        print(f"Node {node_id} created at ({x}, {y})")

    def boundingRect(self):
        return QRectF(-self.radius, -self.radius, 2 * self.radius, 2 * self.radius)

    def paint(self, painter, option, widget):
        painter.setPen(QPen(Qt.black, 1))
        painter.setBrush(QBrush(Qt.black))
        painter.drawEllipse(self.boundingRect())

# Base class for circuit elements
class CircuitElementItem(QGraphicsItem):
    def __init__(self, element_id, node1, node2):
        super().__init__()
        self.element_id = element_id
        self.node1 = node1
        self.node2 = node2
        self.setPos(0, 0)
        print(f"Element {element_id} created between {node1.node_id} and {node2.node_id}")

    def boundingRect(self):
        x1, y1 = self.node1.pos().x(), self.node1.pos().y()
        x2, y2 = self.node2.pos().x(), self.node2.pos().y()
        width = abs(x2 - x1) + 20
        height = abs(y2 - y1) + 20
        return QRectF(min(x1, x2) - 10, min(y1, y2) - 10, width, height)

    def is_horizontal(self):
        x1, y1 = self.node1.pos().x(), self.node1.pos().y()
        x2, y2 = self.node2.pos().x(), self.node2.pos().y()
        return abs(x1 - x2) > abs(y1 - y2)

# Resistor graphics item
class ResistorItem(CircuitElementItem):
    def paint(self, painter, option, widget):
        painter.setPen(QPen(Qt.red, 2))  # Use red for visibility
        x1, y1 = self.node1.pos().x(), self.node1.pos().y()
        x2, y2 = self.node2.pos().x(), self.node2.pos().y()
        if self.is_horizontal():
            painter.drawLine(x1, y1, x1 + (x2 - x1) * 0.25, y1)
            points = [
                QPointF(x1 + (x2 - x1) * 0.25, y1),
                QPointF(x1 + (x2 - x1) * 0.35, y1 + 10),
                QPointF(x1 + (x2 - x1) * 0.45, y1 - 10),
                QPointF(x1 + (x2 - x1) * 0.55, y1 + 10),
                QPointF(x1 + (x2 - x1) * 0.65, y1 - 10),
                QPointF(x1 + (x2 - x1) * 0.75, y1)
            ]
            painter.drawPolyline(points)
            painter.drawLine(x1 + (x2 - x1) * 0.75, y1, x2, y2)
        else:
            painter.drawLine(x1, y1, x1, y1 + (y2 - y1) * 0.25)
            points = [
                QPointF(x1, y1 + (y2 - y1) * 0.25),
                QPointF(x1 + 10, y1 + (y2 - y1) * 0.35),
                QPointF(x1 - 10, y1 + (y2 - y1) * 0.45),
                QPointF(x1 + 10, y1 + (y2 - y1) * 0.55),
                QPointF(x1 - 10, y1 + (y2 - y1) * 0.65),
                QPointF(x1, y1 + (y2 - y1) * 0.75)
            ]
            painter.drawPolyline(points)
            painter.drawLine(x1, y1 + (y2 - y1) * 0.75, x2, y2)

# Inductor graphics item
class InductorItem(CircuitElementItem):
    def paint(self, painter, option, widget):
        painter.setPen(QPen(Qt.blue, 2))  # Use blue for visibility
        x1, y1 = self.node1.pos().x(), self.node1.pos().y()
        x2, y2 = self.node2.pos().x(), self.node2.pos().y()
        if self.is_horizontal():
            painter.drawLine(x1, y1, x1 + (x2 - x1) * 0.25, y1)
            for i in range(4):
                rect = QRectF(
                    x1 + (x2 - x1) * (0.25 + i * 0.125),
                    y1 - 10,
                    (x2 - x1) * 0.125,
                    20
                )
                painter.drawArc(rect, 0, 180 * 16)
            painter.drawLine(x1 + (x2 - x1) * 0.75, y1, x2, y2)
        else:
            painter.drawLine(x1, y1, x1, y1 + (y2 - y1) * 0.25)
            for i in range(4):
                rect = QRectF(
                    x1 - 10,
                    y1 + (y2 - y1) * (0.25 + i * 0.125),
                    20,
                    (y2 - y1) * 0.125
                )
                painter.drawArc(rect, 90 * 16, 180 * 16)
            painter.drawLine(x1, y1 + (y2 - y1) * 0.75, x2, y2)

# Capacitor graphics item
class CapacitorItem(CircuitElementItem):
    def paint(self, painter, option, widget):
        painter.setPen(QPen(Qt.green, 2))  # Use green for visibility
        x1, y1 = self.node1.pos().x(), self.node1.pos().y()
        x2, y2 = self.node2.pos().x(), self.node2.pos().y()
        if self.is_horizontal():
            mid_x = (x1 + x2) / 2
            painter.drawLine(x1, y1, mid_x - 10, y1)
            painter.drawLine(mid_x - 10, y1 - 15, mid_x - 10, y1 + 15)
            painter.drawLine(mid_x + 10, y1 - 15, mid_x + 10, y1 + 15)
            painter.drawLine(mid_x + 10, y1, x2, y2)
        else:
            mid_y = (y1 + y2) / 2
            painter.drawLine(x1, y1, x1, mid_y - 10)
            painter.drawLine(x1 - 15, mid_y - 10, x1 + 15, mid_y - 10)
            painter.drawLine(x1 - 15, mid_y + 10, x1 + 15, mid_y + 10)
            painter.drawLine(x1, mid_y + 10, x2, y2)

# Voltage source graphics item
class VoltageSourceItem(CircuitElementItem):
    def paint(self, painter, option, widget):
        painter.setPen(QPen(Qt.black, 2))
        x1, y1 = self.node1.pos().x(), self.node1.pos().y()
        x2, y2 = self.node2.pos().x(), self.node2.pos().y()
        if self.is_horizontal():
            mid_x = (x1 + x2) / 2
            painter.drawLine(x1, y1, mid_x - 20, y1)
            painter.drawEllipse(QRectF(mid_x - 10, y1 - 10, 20, 20))
            painter.drawLine(mid_x - 5, y1, mid_x + 5, y1)  # -
            painter.drawLine(mid_x, y1 - 5, mid_x, y1 + 5)  # +
            painter.drawLine(mid_x + 20, y1, x2, y2)
        else:
            mid_y = (y1 + y2) / 2
            painter.drawLine(x1, y1, x1, mid_y - 20)
            painter.drawEllipse(QRectF(x1 - 10, mid_y - 10, 20, 20))
            painter.drawLine(x1 - 5, mid_y, x1 + 5, mid_y)  # -
            painter.drawLine(x1, mid_y - 5, x1, mid_y + 5)  # +
            painter.drawLine(x1, mid_y + 20, x2, y2)

# Main window
class CircuitView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RLC Circuit Diagram")
        self.setGeometry(100, 100, 800, 600)

        # Set up graphics view and scene
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene, self)
        self.setCentralWidget(self.view)
        self.view.setRenderHint(QPainter.Antialiasing)

        # Set a default scene rectangle
        self.scene.setSceneRect(0, 0, 400, 400)
        print("Scene initialized with rect:", self.scene.sceneRect())

        # Load circuit
        self.load_circuit("circuit.txt")

        # Debug scene content
        print(f"Scene contains {len(self.scene.items())} items")

    def load_circuit(self, filename):
        try:
            tree = ET.parse(filename)
            root = tree.getroot()
            print("Circuit file parsed successfully")

            # Dictionary to store nodes by ID
            nodes = {}

            # Process nodes
            for node_elem in root.findall("node"):
                node_id = node_elem.get("id")
                x = float(node_elem.get("x"))
                y = float(node_elem.get("y"))
                node_item = NodeItem(node_id, x, y)
                nodes[node_id] = node_item
                self.scene.addItem(node_item)

            # Process circuit elements
            for elem in root:
                if elem.tag in ["resistor", "inductor", "capacitor", "voltagesource"]:
                    elem_id = elem.get("id")
                    node1_id = elem.get("node1")
                    node2_id = elem.get("node2")
                    node1 = nodes.get(node1_id)
                    node2 = nodes.get(node2_id)
                    if node1 and node2:
                        if elem.tag == "resistor":
                            item = ResistorItem(elem_id, node1, node2)
                        elif elem.tag == "inductor":
                            item = InductorItem(elem_id, node1, node2)
                        elif elem.tag == "capacitor":
                            item = CapacitorItem(elem_id, node1, node2)
                        elif elem.tag == "voltagesource":
                            item = VoltageSourceItem(elem_id, node1, node2)
                        self.scene.addItem(item)
                    else:
                        print(f"Warning: Nodes {node1_id} or {node2_id} not found for {elem_id}")

            # Update scene rectangle to include all items
            self.scene.setSceneRect(self.scene.itemsBoundingRect().adjusted(-50, -50, 50, 50))
            print("Updated scene rect:", self.scene.sceneRect())

            # Fit view to content
            self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
            self.view.scale(0.8, 0.8)  # Slightly zoom out for padding
        except FileNotFoundError:
            print(f"Error: {filename} not found")
        except ET.ParseError:
            print(f"Error: Invalid XML format in {filename}")
        except Exception as e:
            print(f"Error loading circuit: {e}")

# Application entry point
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CircuitView()
    window.show()
    sys.exit(app.exec_())
