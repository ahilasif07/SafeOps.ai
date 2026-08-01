import random
from typing import Dict, Any

class SensorGenerator:
    @staticmethod
    def generate_reading(sensor_type: str, force_anomaly: bool = False) -> Dict[str, Any]:
        if sensor_type == "TEMPERATURE":
            unit = "C"
            val = random.uniform(95.0, 125.0) if force_anomaly else random.uniform(55.0, 75.0)
            is_anomaly = val > 90.0
        elif sensor_type == "PRESSURE":
            unit = "PSI"
            val = random.uniform(140.0, 180.0) if force_anomaly else random.uniform(80.0, 110.0)
            is_anomaly = val > 130.0
        elif sensor_type == "VIBRATION":
            unit = "mm/s"
            val = random.uniform(8.5, 15.0) if force_anomaly else random.uniform(1.0, 4.0)
            is_anomaly = val > 7.0
        elif sensor_type == "TOXIC_GAS":
            unit = "ppm"
            val = random.uniform(15.0, 45.0) if force_anomaly else random.uniform(0.0, 3.0)
            is_anomaly = val > 10.0
        else:
            unit = "BOOL"
            val = 1.0 if force_anomaly else 0.0
            is_anomaly = bool(val)

        return {
            "sensor_type": sensor_type,
            "value": round(val, 2),
            "unit": unit,
            "is_anomaly": is_anomaly
        }
