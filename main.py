from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QFrame
from PyQt6.QtCore import QLocale
from cslaser_widget import CSLaserWidget


def main():
    app = QApplication([])

    QLocale.setDefault(QLocale.c())

    win = QWidget()
    win.setWindowTitle("Optris Pyrometer CSLaser")
    win.resize(400, 400)
    layout = QHBoxLayout()
    frame = QFrame()
    frame_layout = QHBoxLayout(frame)
    polling_interval = 0.5 # sec
    pyrometer_widget = CSLaserWidget(polling_interval=polling_interval)
    frame_layout.addWidget(pyrometer_widget)
    layout.addWidget(frame)

    polling_interval = 0.5 # sec
    pyrometer_widget = CSLaserWidget(polling_interval=polling_interval)

    win.setLayout(layout)
    win.show()

    app.exec()


if __name__ == "__main__":
    main()