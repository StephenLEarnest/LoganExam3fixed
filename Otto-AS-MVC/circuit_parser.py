import xml.etree.ElementTree as ET

class CircuitParser:
    def __init__(self, filename):
        self.filename = filename
        self.nodes = {}
        self.elements = []

    def parse(self):  # <--- THIS is the method you’re missing!
        tree = ET.parse(self.filename)
        root = tree.getroot()

        for node in root.findall('node'):
            node_id = node.get('id')
            x = int(node.get('x'))
            y = int(node.get('y'))
            self.nodes[node_id] = (x, y)

        for tag in ['resistor', 'capacitor', 'inductor', 'voltagesource']:
            for elem in root.findall(tag):
                self.elements.append({
                    'type': tag,
                    'id': elem.get('id'),
                    'from': elem.get('from'),
                    'to': elem.get('to')
                })

        return self.nodes, self.elements
