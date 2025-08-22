from dataclasses import dataclass, asdict
from datetime import datetime


class DataCollector:
    def __init__(self, pyrometer_widget):
        self.pyrometer_widget = pyrometer_widget


    def collect_data(self) -> dict:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        temperature = self.pyrometer_widget.last_temperature
        return {"timestamp": timestamp, "temperature": temperature}