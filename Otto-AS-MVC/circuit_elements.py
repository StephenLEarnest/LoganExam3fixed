from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import QRectF, Qt, QPointF
import math

class CircuitElement(QGraphicsItem):
    def __init__(self, start, end):
        super().__init__()
        self.start = QPointF(*start)
        self.end = QPointF(*end)
        self.setZValue(1)

    def boundingRect(self):
        return QRectF(self.start, self.end).normalized().adjusted(-10, -10, 10, 10)

    def draw_line(self, painter):
        painter.setPen(QPen(Qt.black, 2))
        painter.drawLine(self.start, self.end)

    def angle_and_distance(self):
        dx = self.end.x() - self.start.x()
        dy = self.end.y() - self.start.y()
        angle = math.atan2(dy, dx)
        length = math.hypot(dx, dy)
        return angle, length

class Resistor(CircuitElement):
    def paint(self, painter, option, widget=None):
        self.draw_line(painter)
        angle, length = self.angle_and_distance()
        mid = (self.start + self.end) / 2
        painter.save()
        painter.translate(mid)
        painter.rotate(math.degrees(angle))
        painter.drawRect(-10, -5, 20, 10)
        painter.restore()

class Capacitor(CircuitElement):
    def paint(self, painter, option, widget=None):
        self.draw_line(painter)
        angle, length = self.angle_and_distance()
        mid = (self.start + self.end) / 2
        painter.save()
        painter.translate(mid)
        painter.rotate(math.degrees(angle))
        painter.drawLine(-10, -10, -10, 10)
        painter.drawLine(10, -10, 10, 10)
        painter.restore()

class Inductor(CircuitElement):
    def paint(self, painter, option, widget=None):
        self.draw_line(painter)
        angle, length = self.angle_and_distance()
        mid = (self.start + self.end) / 2
        painter.save()
        painter.translate(mid)
        painter.rotate(math.degrees(angle))
        radius = 5
        for i in range(-2, 3):
            painter.drawArc(i * radius * 2, -radius, radius * 2, radius * 2, 0, 180 * 16)
        painter.restore()

class VoltageSource(CircuitElement):
    def paint(self, painter, option, widget=None):
        self.draw_line(painter)
        angle, length = self.angle_and_distance()
        mid = (self.start + self.end) / 2
        painter.save()
        painter.translate(mid)
        painter.rotate(math.degrees(angle))
        painter.drawEllipse(-10, -10, 20, 20)
        painter.drawText(-3, 5, "+")
        painter.drawText(-3, -5, "-")
        painter.restore()
