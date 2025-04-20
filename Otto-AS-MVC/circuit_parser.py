import re
from PyQt5.QtCore import QPointF
from components import ResistorItem, CapacitorItem, InductorItem, VoltageSourceItem

class CircuitParser:
    def __init__(self, scene):
        self.scene = scene
        self.nodes = {}

    def parse_file(self, file_path):
        with open(file_path, 'r') as f:
            content = f.read()

        # Parse nodes
        node_matches = re.findall(r'<node name="(.*?)" x="(.*?)" y="(.*?)"/>', content)
        for name, x, y in node_matches:
            point = QPointF(float(x), float(y))
            self.nodes[name] = point

        # Parse components
        element_types = {
            'resistor': ResistorItem,
            'capacitor': CapacitorItem,
            'inductor': InductorItem,
            'voltage_source': VoltageSourceItem
        }

        for tag, cls in element_types.items():
            pattern = fr'<{tag} name=".*?" node1="(.*?)" node2="(.*?)"/>'
            for node1, node2 in re.findall(pattern, content):
                p1 = self.nodes.get(node1)
                p2 = self.nodes.get(node2)
                if p1 and p2:
                    item = cls(p1, p2)
                    self.scene.addItem(item)

