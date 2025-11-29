class VitalsMonitor:
    def __init__(self):
        self.thresholds = {
            "heart_rate": (60, 100),
            "spo2": (95, 100),
            "sys_bp": (90, 140),  # Simplified
            "dia_bp": (60, 90),  # Simplified
            "temperature": (36.1, 37.5)
        }

    def check_vitals(self, vitals):
        """Checks vitals against thresholds. Returns status, analysis, and per-vital details."""
        status = "NORMAL"
        abnormalities = []
        details = {}

        # Check Heart Rate
        if not (self.thresholds["heart_rate"][0] <= vitals["heart_rate"] <= self.thresholds["heart_rate"][1]):
            abnormalities.append(f"Heart Rate: {vitals['heart_rate']} bpm (Normal: 60-100)")
            details["heart_rate"] = "ABNORMAL"
        else:
            details["heart_rate"] = "NORMAL"

        # Check SpO2
        if not (self.thresholds["spo2"][0] <= vitals["spo2"] <= self.thresholds["spo2"][1]):
            abnormalities.append(f"SpO2: {vitals['spo2']}% (Normal: 95-100)")
            details["spo2"] = "ABNORMAL"
        else:
            details["spo2"] = "NORMAL"

        # Check BP (Check both sys and dia)
        sys_abnormal = not (self.thresholds["sys_bp"][0] <= vitals["sys_bp"] <= self.thresholds["sys_bp"][1])
        dia_abnormal = not (self.thresholds["dia_bp"][0] <= vitals["dia_bp"] <= self.thresholds["dia_bp"][1])

        if sys_abnormal:
            abnormalities.append(f"Systolic BP: {vitals['sys_bp']} mmHg (Normal: 90-140)")
        if dia_abnormal:
            abnormalities.append(f"Diastolic BP: {vitals['dia_bp']} mmHg (Normal: 60-90)")

        if sys_abnormal or dia_abnormal:
            details["bp"] = "ABNORMAL"
        else:
            details["bp"] = "NORMAL"

        # Check Temperature
        if not (self.thresholds["temperature"][0] <= vitals["temperature"] <= self.thresholds["temperature"][1]):
            abnormalities.append(f"Temperature: {vitals['temperature']}°C (Normal: 36.1-37.5)")
            details["temperature"] = "ABNORMAL"
        else:
            details["temperature"] = "NORMAL"

        if abnormalities:
            status = "ABNORMAL"

        return {
            "status": status,
            "abnormalities": abnormalities,
            "details": details
        }
