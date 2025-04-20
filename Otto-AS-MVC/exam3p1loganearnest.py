import sys
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QFormLayout, QLineEdit,
    QGroupBox, QLabel, QPushButton, QHBoxLayout
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar
)
from matplotlib.figure import Figure
from scipy.integrate import solve_ivp


class RLCGui(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RLC Circuit Simulator")

        main_layout = QVBoxLayout()

        # --- Circuit Diagram GroupBox ---
        circuit_box = QGroupBox("RLC Circuit Diagram")
        circuit_layout = QVBoxLayout()
        pixmap = QPixmap("Circuit1.png")  # Ensure this path is correct
        circuit_label = QLabel()
        circuit_label.setPixmap(pixmap)
        circuit_label.setAlignment(Qt.AlignCenter)
        circuit_layout.addWidget(circuit_label)
        circuit_box.setLayout(circuit_layout)
        main_layout.addWidget(circuit_box)

        # --- Form Layout for Inputs ---
        form_layout = QFormLayout()
        self.R_input = QLineEdit("10")
        self.L_input = QLineEdit("20")
        self.C_input = QLineEdit("0.05")
        self.mag_input = QLineEdit("20")
        self.freq_input = QLineEdit("20")  # In rad/s as per v(t) = Vm * sin(ωt + φ)
        self.phase_input = QLineEdit("0")

        form_layout.addRow("Resistance R (Ω):", self.R_input)
        form_layout.addRow("Inductance L (H):", self.L_input)
        form_layout.addRow("Capacitance C (F):", self.C_input)
        form_layout.addRow("Voltage Magnitude (Vm):", self.mag_input)
        form_layout.addRow("Voltage Frequency (ω in rad/s):", self.freq_input)
        form_layout.addRow("Voltage Phase (φ in rad):", self.phase_input)

        main_layout.addLayout(form_layout)

        # --- Simulate Button ---
        self.simulate_btn = QPushButton("Simulate")
        self.simulate_btn.clicked.connect(self.simulate_circuit)
        main_layout.addWidget(self.simulate_btn)

        # --- Matplotlib Figure & Toolbar ---
        self.figure = Figure(figsize=(6, 4))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        main_layout.addWidget(self.toolbar)
        main_layout.addWidget(self.canvas)

        self.setLayout(main_layout)

    def simulate_circuit(self):
        try:
            R = float(self.R_input.text())
            L = float(self.L_input.text())
            C = float(self.C_input.text())
            Vm = float(self.mag_input.text())
            omega = float(self.freq_input.text())
            phi = float(self.phase_input.text())

            def v_in(t):
                return Vm * np.sin(omega * t + phi)

            def deriv(t, y):
                i1, vc = y
                di1dt = (v_in(t) - R * i1 - vc) / L
                dvcdt = i1 / C
                return [di1dt, dvcdt]

            t_span = (0, 5)
            t_eval = np.linspace(*t_span, 1000)
            y0 = [0, 0]

            sol = solve_ivp(deriv, t_span, y0, t_eval=t_eval)
            t = sol.t
            i1 = sol.y[0]
            vc = sol.y[1]
            i2 = C * np.gradient(vc, t)

            # Plotting
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.plot(t, i1, label="i₁(t) - Inductor Current")
            ax.plot(t, i2, label="i₂(t) - Capacitor Current")
            ax.plot(t, vc, label="v_c(t) - Capacitor Voltage")
            ax.set_title("Transient Response of RLC Circuit")
            ax.set_xlabel("Time (s)")
            ax.set_ylabel("Amplitude")
            ax.legend()
            ax.grid(True)
            self.canvas.draw()

        except ValueError:
            print("Invalid input detected. Please enter numerical values.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = RLCGui()
    gui.resize(800, 700)
    gui.show()
    sys.exit(app.exec_())

