import csv
from dataclasses import asdict, dataclass
import os
from pathlib import Path

ENCODING = "utf-8"

class DataLogger:
    def __init__(self, csv_path):
        self._csv_path = csv_path


    @property
    def csv_path(self) -> Path:
        return self._csv_path


    def write_csv(self, data_object) -> None:
        data_dict = data_object.to_dict()
        # write header if file not existing
        if not os.path.exists(self._csv_path):
            with open(self._csv_path, "w", newline="", encoding=ENCODING) as f_csv:
                writer = csv.DictWriter(f_csv, fieldnames=data_dict.keys())
                writer.writeheader()
        # add data (create csv file if not existing)
        with open(self._csv_path, "a", newline="", encoding=ENCODING) as f_csv:
            writer = csv.DictWriter(f_csv, fieldnames=data_dict.keys())
            writer.writerow(data_dict)

