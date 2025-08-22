from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QFrame
from PyQt6.QtCore import QLocale
from cslaser_widget import CSLaserWidget
from chart_widget import ChartWidget
from data_collector import DataCollector
from data_logger import DataLogger


def main():
    app = QApplication([])

    QLocale.setDefault(QLocale.c())

    win = QWidget()
    win.setWindowTitle("Optris Pyrometer CSLaser")
    win.resize(800, 500)
    layout = QHBoxLayout()
    frame = QFrame()
    frame_layout = QHBoxLayout(frame)
    polling_interval = 0.5 # sec
    pyrometer_widget = CSLaserWidget(polling_interval=polling_interval)
    data_collector = DataCollector(pyrometer_widget)
    chart_widget = ChartWidget(data_collector)
    frame_layout.addWidget(pyrometer_widget)
    frame_layout.addWidget(chart_widget)
    layout.addWidget(frame)
    layout.addWidget

    polling_interval = 0.5 # sec
    pyrometer_widget = CSLaserWidget(polling_interval=polling_interval)

    win.setLayout(layout)
    win.show()

    app.exec()


if __name__ == "__main__":
    main()