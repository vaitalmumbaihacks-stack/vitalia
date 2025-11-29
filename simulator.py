import random
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class VitalsSimulator:
    def __init__(self):
        self.heart_rate = 75
        self.spo2 = 98
        self.sys_bp = 120
        self.dia_bp = 80
        self.temperature = 37.0

    def generate_vitals(self, abnormal_flags=None):
        """Generates next set of vitals.
        abnormal_flags: dict with keys 'hr', 'spo2', 'bp', 'temp' set to True/False"""

        if abnormal_flags is None:
            abnormal_flags = {}

        # Heart Rate
        if not abnormal_flags.get('hr', False):
            self.heart_rate = int(max(60, min(100, self.heart_rate + random.randint(-5, 5))))
        else:
            self.heart_rate = random.choice([random.randint(40, 55), random.randint(110, 150)])

        # SpO2
        if not abnormal_flags.get('spo2', False):
            self.spo2 = int(max(95, min(100, self.spo2 + random.randint(-1, 1))))
        else:
            self.spo2 = random.randint(85, 94)

        # BP
        if not abnormal_flags.get('bp', False):
            self.sys_bp = int(max(110, min(130, self.sys_bp + random.randint(-2, 2))))
            self.dia_bp = int(max(70, min(85, self.dia_bp + random.randint(-2, 2))))
        else:
            self.sys_bp = random.randint(140, 180)
            self.dia_bp = random.randint(90, 110)

        # Temperature
        if not abnormal_flags.get('temp', False):
            self.temperature = round(max(36.5, min(37.5, self.temperature + random.uniform(-0.1, 0.1))), 1)
        else:
            self.temperature = round(random.choice([random.uniform(38.0, 40.0), random.uniform(35.0, 36.0)]), 1)

        return {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "heart_rate": self.heart_rate,
            "spo2": self.spo2,
            "sys_bp": self.sys_bp,
            "dia_bp": self.dia_bp,
            "temperature": self.temperature
        }
