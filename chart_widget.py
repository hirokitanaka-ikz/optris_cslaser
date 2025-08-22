from PyQt6.QtWidgets import (
    QGroupBox, QPushButton, QFileDialog, QMessageBox, QVBoxLayout, QFormLayout,
    QSpinBox
)
from PyQt6.QtCore import QTimer
from data_logger import DataLogger
import numpy as np
import pyqtgraph as pg
from pathlib import Path
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def default_filename() -> str:
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{now}_pyrometer"


class ChartWidget(QGroupBox):
    def __init__(self, data_collector, parent=None):
        super().__init__("Temperature Chart", parent)
        self.collector = data_collector
        self.record_timer = None
        self.start_timestamp = None


        # UI elements
        self.record_interval_spin = QSpinBox()
        self.record_interval_spin.setRange(1, 600) # sec
        self.record_interval_spin.setSingleStep(1)
        self.record_interval_spin.setSuffix("sec")
        self.record_btn = QPushButton("Start Record")
        self.record_btn.clicked.connect(self.toggle_record)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground("w")
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setLabel("left", "T", units="°C")
        self.plot_widget.setLabel("bottom", "Time", units="min")

        # layout
        layout = QVBoxLayout()
        record_form = QFormLayout()
        record_form.addRow("Record Interval", self.record_interval_spin)
        record_form.addRow("", self.record_btn)
        layout.addLayout(record_form)
        layout.addWidget(self.plot_widget)
        self.setLayout(layout)


    def initialize_chart(self):
        self.x_data = []
        self.y_data = []
        self.strat_time = None
        self.plot = self.plot_widget.plot(pen="b")
    

    def __del__(self):
        try:
            self.record_timer.stop()
        except Exception:
            pass
    

    def write_data(self) -> None:
        data_dict = self.data_collector.collect_data()
        self.data_logger.write_csv(data_dict)
        try:
            timestamp = datetime.fromisoformat(data_dict["timestamp"])
            temperature = data_dict["temperature"]
            if self.start_timestamp is None:
                self.start_timestamp = timestamp
            elapsed_min = (timestamp - self.start_timestamp).total_seconds() / 60.0
            self.x_data.append(elapsed_min)
            self.y_data.append(temperature)
        except Exception as e:
            logging.error(f"Fail to plot data: {e}")
            return


    def toggle_record(self):
        if self.record_timer is None:
            folder = QFileDialog.getExistingDirectory(self, "Select Folder to Save Data")
            if not folder:
                QMessageBox.warning(self, "Warning", "No folder selected.")
                return
            folder_path = Path(folder)
            default_name = default_filename()
            csv_path = folder_path / f"{default_name}.csv"
            self.data_logger = DataLogger(csv_path)
            # write first data
            self.write_data()
            self.initialize_chart()
            self.record_timer = QTimer(self)
            self.record_timer.timeout.connect(self.write_data)
            try:
                self.record_timer.start(int(self.record_interval_spin.value() * 1000)) # sec -> millisec
            except TypeError as e:
                logging.error(f"Failed to start timer: {e}")
                self.record_timer = None
                return
            self.record_btn.setText("Stop Record")
            QMessageBox.information(self, "Recording Start", f"save path: \n{self.data_logger.csv_path}\n{self.data_logger.yml_path}\n\nRecording start")
            logging.info("LITMoS data recording started")
        else:
            self.record_timer.stop()
            self.record_timer = None
            QMessageBox.information(self, "Recording Stop", f"save path: \n{self.data_logger.csv_path}\n{self.data_logger.yml_path}\n\nRecording stop")
            logging.info("LITMoS data recording stopped")
            self.record_btn.setText("Start Record")

