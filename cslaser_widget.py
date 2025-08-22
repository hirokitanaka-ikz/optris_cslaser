from PyQt6.QtWidgets import (
    QGroupBox, QPushButton, QLabel, QVBoxLayout, QHBoxLayout,
    QComboBox, QDoubleSpinBox, QFormLayout, QMessageBox
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont
from optris_cslaser_control import OptrisCSLaserControl
from base_polling_thread import BasePollingThread
import serial.tools.list_ports
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class CSLaserWidget(QGroupBox):
    """
    Control widget for Optris CS Laser
    """

    def __init__(self, parent=None, polling_interval=0.5):
        super().__init__(parent)
        self.setTitle("Optris CS Laser Control")
        self.pyro = None
        self.polling_thread = None
        self.polling_interval = polling_interval

        # UI Elements
        self.scan_port_btn = QPushButton("Scan COM Port")
        self.scan_port_btn.clicked.connect(self.scan_com_port)
        self.ports_combo = QComboBox()
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.toggle_connect)

        self.laser_btn = QPushButton("Laser ON/OFF")
        self.laser_btn.setEnabled(False)
        self.laser_btn.clicked.connect(self.toggle_laser)

        self.emissivity_label = QLabel("Emissivity: -.--")
        self.emissivity_input = QDoubleSpinBox()
        self.emissivity_input.setRange(0.0, 1.0)
        self.emissivity_input.setValue(0.8)
        self.emissivity_input.setSingleStep(0.01)
        self.emissivity_input.setEnabled(False)
        self.emissivity_change_btn = QPushButton("Change Emissivity")
        self.emissivity_change_btn.setEnabled(False)
        self.emissivity_change_btn.clicked.connect(self.change_emissivity)

        self.temperature_label = QLabel("T = ---.-°C")
        self.temperature_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(36)
        font.setBold(True)
        self.temperature_label.setFont(font)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.scan_port_btn)
        layout.addWidget(self.ports_combo)
        layout.addWidget(self.connect_btn)
        layout.addWidget(self.laser_btn)
        layout.addWidget(self.emissivity_label)
        emissivity_input_layout = QHBoxLayout()
        emissivity_input_layout.addWidget(self.emissivity_input)
        emissivity_input_layout.addWidget(self.emissivity_change_btn)
        layout.addLayout(emissivity_input_layout)
        layout.addWidget(self.temperature_label)
        self.setLayout(layout)
    

    def scan_com_port(self):
        self.ports_combo.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.ports_combo.addItem(f"{port.description}", port.device)
    

    def toggle_connect(self):
        if self.pyro is None:
            # connect
            port = self.ports_combo.currentData()
            if port is None:
                QMessageBox.warning(self, "Warning", "Please select a COM port.")
                return
            try:
                self.pyro = OptrisCSLaserControl(port=port)
            except Exception as e:
                logging.error(f"Failed to create OptrisCSLaserControl instance: {e}")
                return
            try:
                self.pyro.connect()
                self.scan_port_btn.setEnabled(False)
                self.ports_combo.setEnabled(False)
                self.connect_btn.setText("Disconnect")
                self.laser_btn.setEnabled(True)
                self.emissivity_label.setText(f"Emissivity: {self.pyro.emissivity:.2f}")
                self.emissivity_input.setValue(self.pyro.emissivity)
                self.emissivity_input.setEnabled(True)
                self.emissivity_change_btn.setEnabled(True)
                self.pyro.laser = False # ensure laser to be off
            except Exception as e:
                logging.error(f"Failed to connect to OptrisCSLaserControl: {e}")
                return
            # start polling
            try:
                self.polling_thread = CSLaserPollingThread(self.pyro, self.polling_interval, parent=self)
                self.polling_thread.updated.connect(self.update_temperature_display)
                self.polling_thread.start()
            except Exception as e:
                logging.error(f"Failed to start polling thread: {e}")
                return
        else:
            # disconnect
            if self.polling_thread is not None:
                self.polling_thread.stop()
                self.polling_thread = None
            try:
                self.pyro.disconnect()
                self.pyro = None
            except Exception as e:
                return
            self.scan_port_btn.setEnabled(True)
            self.ports_combo.setEnabled(True)
            self.connect_btn.setText("Connect")
            self.laser_btn.setEnabled(False)
            self.emissivity_label.setText("Emissivity: -.--")
            self.emissivity_input.setEnabled(False)
            self.emissivity_change_btn.setEnabled(False)


    def toggle_laser(self):
        if self.polling_thread is not None:
            self.polling_thread.stop()
        if self.pyro.laser:
            # if laser is on -> off
            self.pyro.laser = False
        else:
            # if laser is off -> on
            self.pyro.laser = True
        self.polling_thread.start()


    def change_emissivity(self):
        if self.polling_thread is not None:
            self.polling_thread.stop()
        self.pyro.emissivity = self.emissivity_input.value()
        self.polling_thread.start()


    def update_emissivity_display(self):
        if self.polling_thread is not None:
            self.polling_thread.stop()
        emissivity = self.pyro.emissivity
        self.polling_thread.start()
        self.emissivity_label.setText(f"Current Emissivity: {emissivity:.2f}")
        self.emissivity_input.setValue(emissivity)


    def update_temperature_display(self, temperature: float):
        self.temperature_label.setText(f"T = {temperature:.1f}°C")



class CSLaserPollingThread(BasePollingThread):
    updated = pyqtSignal(float)

    def get_data(self) -> float:
        return self.controller.target_temperature
    

    def emit_data(self, data:float) -> None:
        self.updated.emit(data)
