# cycle_simulator.py
import sys
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QComboBox, QRadioButton, QButtonGroup)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg


class Air:
    def __init__(self):
        self.R = 0.287  # kJ/kg·K
        self.gamma = 1.4
        self.cp = self.gamma * self.R / (self.gamma - 1)
        self.cv = self.R / (self.gamma - 1)
        self.reset()

    def reset(self):
        self.T = 273.15  # K
        self.P = 101.325  # kPa
        self.v = (self.R * self.T) / self.P  # Ideal gas law

    def set_state(self, T=None, P=None, v=None):
        if T and P:
            self.T = T
            self.P = P
            self.v = (self.R * T) / P
        elif T and v:
            self.T = T
            self.v = v
            self.P = (self.R * T) / v
        elif P and v:
            self.P = P
            self.v = v
            self.T = (P * v) / self.R


class CycleModel:
    def __init__(self):
        self.air = Air()
        self.states = {}

    def calculate_otto(self, T1, P1, r):
        self.air.reset()
        self.air.set_state(T=T1, P=P1)
        self.states = {'1': (self.air.T, self.air.P, self.air.v)}

        # 1-2: Isentropic compression
        self.air.P *= r ** self.air.gamma
        self.air.T *= r ** (self.air.gamma - 1)
        self.air.v /= r
        self.states['2'] = (self.air.T, self.air.P, self.air.v)

        # 2-3: Constant volume heat addition
        Q_in = 1000  # Simplified heat addition (kJ/kg)
        self.air.T += Q_in / self.air.cv
        self.air.P = (self.air.R * self.air.T) / self.air.v
        self.states['3'] = (self.air.T, self.air.P, self.air.v)

        # 3-4: Isentropic expansion
        self.air.P /= r ** self.air.gamma
        self.air.T /= r ** (self.air.gamma - 1)
        self.air.v *= r
        self.states['4'] = (self.air.T, self.air.P, self.air.v)

        return self._calculate_metrics('otto')

    def calculate_diesel(self, T1, P1, r, rc):
        self.air.reset()
        self.air.set_state(T=T1, P=P1)
        self.states = {'1': (self.air.T, self.air.P, self.air.v)}

        # 1-2: Isentropic compression
        self.air.P *= r ** self.air.gamma
        self.air.T *= r ** (self.air.gamma - 1)
        self.air.v /= r
        self.states['2'] = (self.air.T, self.air.P, self.air.v)

        # 2-3: Constant pressure expansion
        self.air.v *= rc
        self.air.T = (self.air.v * self.air.P) / self.air.R
        self.states['3'] = (self.air.T, self.air.P, self.air.v)

        # 3-4: Isentropic expansion
        expansion_ratio = r / rc
        self.air.P /= expansion_ratio ** self.air.gamma
        self.air.T /= expansion_ratio ** (self.air.gamma - 1)
        self.air.v *= expansion_ratio
        self.states['4'] = (self.air.T, self.air.P, self.air.v)

        return self._calculate_metrics('diesel')

    def _calculate_metrics(self, cycle_type):
        T1 = self.states['1'][0]
        T2 = self.states['2'][0]
        T3 = self.states['3'][0]
        T4 = self.states['4'][0]

        if cycle_type == 'otto':
            Q_in = self.air.cv * (T3 - T2)
        elif cycle_type == 'diesel':
            Q_in = self.air.cp * (T3 - T2)

        Q_out = self.air.cv * (T4 - T1)
        W_net = Q_in - Q_out
        efficiency = W_net / Q_in

        return {
            'efficiency': efficiency,
            'W_net': W_net,
            'Q_in': Q_in,
            'states': self.states
        }


class CycleView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Thermodynamic Cycle Simulator')
        self.setGeometry(100, 100, 1000, 800)
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Control Panel
        control_panel = QHBoxLayout()
        self.cycle_type = QButtonGroup()
        self.otto_btn = QRadioButton("Otto Cycle")
        self.diesel_btn = QRadioButton("Diesel Cycle")
        self.cycle_type.addButton(self.otto_btn)
        self.cycle_type.addButton(self.diesel_btn)
        self.otto_btn.setChecked(True)

        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["SI Units", "English Units"])

        control_panel.addWidget(QLabel("Cycle Type:"))
        control_panel.addWidget(self.otto_btn)
        control_panel.addWidget(self.diesel_btn)
        control_panel.addWidget(QLabel("Unit System:"))
        control_panel.addWidget(self.unit_combo)

        # Input Fields
        self.input_labels = {
            'T1': QLabel("T1 (K)"),
            'P1': QLabel("P1 (kPa)"),
            'r': QLabel("Compression Ratio (r)"),
            'rc': QLabel("Cutoff Ratio (rc)")
        }
        self.inputs = {
            'T1': QLineEdit('300'),
            'P1': QLineEdit('100'),
            'r': QLineEdit('8'),
            'rc': QLineEdit('2')
        }

        input_grid = QHBoxLayout()
        for param in ['T1', 'P1', 'r', 'rc']:
            container = QVBoxLayout()
            container.addWidget(self.input_labels[param])
            container.addWidget(self.inputs[param])
            input_grid.addLayout(container)

        self.inputs['rc'].setVisible(False)
        self.input_labels['rc'].setVisible(False)

        # Results Display
        self.result_labels = {
            'W_net': QLabel("Net Work:"),
            'Q_in': QLabel("Heat Input:"),
            'efficiency': QLabel("Efficiency:")
        }
        self.results = {
            'W_net': QLineEdit(),
            'Q_in': QLineEdit(),
            'efficiency': QLineEdit()
        }

        results_grid = QHBoxLayout()
        for param in ['W_net', 'Q_in', 'efficiency']:
            container = QVBoxLayout()
            container.addWidget(self.result_labels[param])
            container.addWidget(self.results[param])
            results_grid.addLayout(container)
            self.results[param].setReadOnly(True)

        # Plot Canvas
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvasQTAgg(self.figure)

        # Calculate Button
        self.calc_btn = QPushButton("Calculate Cycle")

        # Assemble Layout
        layout.addLayout(control_panel)
        layout.addLayout(input_grid)
        layout.addLayout(results_grid)
        layout.addWidget(self.canvas)
        layout.addWidget(self.calc_btn)


class CycleController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.current_unit_system = "SI Units"
        self.connect_signals()

    def connect_signals(self):
        self.view.calc_btn.clicked.connect(self.calculate)
        self.view.diesel_btn.toggled.connect(self.toggle_cutoff_ratio)
        self.view.unit_combo.currentIndexChanged.connect(self.handle_unit_change)

    def toggle_cutoff_ratio(self, checked):
        self.view.inputs['rc'].setVisible(checked)
        self.view.input_labels['rc'].setVisible(checked)

    def handle_unit_change(self):
        new_unit = self.view.unit_combo.currentText()
        if new_unit != self.current_unit_system:
            self.convert_inputs(self.current_unit_system, new_unit)
            self.current_unit_system = new_unit
            self.update_unit_labels()

    def convert_inputs(self, old_unit, new_unit):
        # Temperature conversion
        try:
            t1 = float(self.view.inputs['T1'].text())
            if old_unit == "SI Units":
                t1 = (t1 - 273.15) * 9 / 5 + 32  # K to °F
            else:
                t1 = (t1 - 32) * 5 / 9 + 273.15  # °F to K
            self.view.inputs['T1'].setText(f"{t1:.2f}")
        except ValueError:
            pass

        # Pressure conversion
        try:
            p1 = float(self.view.inputs['P1'].text())
            if old_unit == "SI Units":
                p1 /= 6.89476  # kPa to psi
            else:
                p1 *= 6.89476  # psi to kPa
            self.view.inputs['P1'].setText(f"{p1:.2f}")
        except ValueError:
            pass

    def update_unit_labels(self):
        if self.current_unit_system == "SI Units":
            self.view.input_labels['T1'].setText("T1 (K)")
            self.view.input_labels['P1'].setText("P1 (kPa)")
        else:
            self.view.input_labels['T1'].setText("T1 (°F)")
            self.view.input_labels['P1'].setText("P1 (psi)")

    def calculate(self):
        try:
            inputs = {
                'T1': float(self.view.inputs['T1'].text()),
                'P1': float(self.view.inputs['P1'].text()),
                'r': float(self.view.inputs['r'].text())
            }

            if self.view.diesel_btn.isChecked():
                inputs['rc'] = float(self.view.inputs['rc'].text())

            if self.current_unit_system == "English Units":
                inputs['T1'] = (inputs['T1'] - 32) * 5 / 9 + 273.15
                inputs['P1'] *= 6.89476

            if self.view.otto_btn.isChecked():
                results = self.model.calculate_otto(**inputs)
            else:
                results = self.model.calculate_diesel(**inputs)

            self.view.results['W_net'].setText(f"{results['W_net']:.2f} kJ/kg")
            self.view.results['Q_in'].setText(f"{results['Q_in']:.2f} kJ/kg")
            self.view.results['efficiency'].setText(f"{results['efficiency']:.1%}")

            self.plot_cycle(results['states'])

        except Exception as e:
            print(f"Error: {e}")

    def plot_cycle(self, states):
        self.view.ax.clear()
        V = [state[2] for state in states.values()]
        P = [state[1] for state in states.values()]
        self.view.ax.plot(V, P, 'b-o')
        self.view.ax.set(xlabel='Specific Volume (m³/kg)',
                         ylabel='Pressure (kPa)',
                         title='P-V Diagram')
        self.view.canvas.draw()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    model = CycleModel()
    view = CycleView()
    controller = CycleController(model, view)
    view.show()
    sys.exit(app.exec_())


