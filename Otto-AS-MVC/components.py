from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtGui import QPen, QPainter
from PyQt5.QtCore import QRectF, Qt, QPointF

class BaseComponent(QGraphicsItem):
    def __init__(self, p1: QPointF, p2: QPointF):
        super().__init__()
        self.p1 = p1
        self.p2 = p2
        self.setZValue(1)  # make sure it's visible

    def boundingRect(self):
        extra = 10
        x1, y1 = self.p1.x(), self.p1.y()
        x2, y2 = self.p2.x(), self.p2.y()
        return QRectF(min(x1, x2), min(y1, y2),
                      abs(x1 - x2), abs(y1 - y2)).adjusted(-extra, -extra, extra, extra)

class ResistorItem(BaseComponent):
    def paint(self, painter: QPainter, option, widget=None):
        painter.setPen(QPen(Qt.black, 2))
        painter.drawLine(self.p1, self.p2)

class CapacitorItem(BaseComponent):
    def paint(self, painter: QPainter, option, widget=None):
        painter.setPen(QPen(Qt.blue, 2))
        mid = (self.p1 + self.p2) / 2
        painter.drawLine(self.p1, self.p2)
        painter.drawLine(mid.x() - 5, mid.y() - 10, mid.x() - 5, mid.y() + 10)
        painter.drawLine(mid.x() + 5, mid.y() - 10, mid.x() + 5, mid.y() + 10)

class InductorItem(BaseComponent):
    def paint(self, painter: QPainter, option, widget=None):
        painter.setPen(QPen(Qt.darkGreen, 2))
        painter.drawLine(self.p1, self.p2)

class VoltageSourceItem(BaseComponent):
    def paint(self, painter: QPainter, option, widget=None):
        painter.setPen(QPen(Qt.red, 2))
        mid = (self.p1 + self.p2) / 2
        painter.drawLine(self.p1, self.p2)
        painter.drawEllipse(mid, 10, 10)
