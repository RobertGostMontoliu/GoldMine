import json
import os
from ui.json_path import resource_path

class Logger:
    def __init__(self, farm_name):
        self.farm_name = farm_name
        self.logs = []

    def log(self, task_name, status):
        log_entry = {"task_name": task_name, "status": status}
        self.logs.append(log_entry)
        print(f"{task_name}: {status}")

    def save_logs(self):
        log_data = {
            "farm_name": self.farm_name,
            "logs": self.logs
        }
        log_path = resource_path("ui\\JSON_FILE\\farm_logs.json")
        with open(log_path, 'w') as log_file:
            json.dump(log_data, log_file, indent=4)