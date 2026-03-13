def detect_anomalies(data: dict) -> list[dict]:
    """
    Checks incoming telemetry payload against static rules.
    Returns a list of alerts if anomalies are found.
    """
    alerts = []
    device_id = data.get("device_id")
    temperature = data.get("temperature", 0.0)
    timestamp = data.get("timestamp")

    if temperature > 45.0:
        alerts.append({
            "device_id": device_id,
            "rule_name": "High Temperature",
            "description": f"Temperature exceeded 45C: {temperature}C",
            "timestamp": timestamp
        })
        
    if data.get("vibration", 0.0) > 4.5:
        alerts.append({
            "device_id": device_id,
            "rule_name": "High Vibration",
            "description": f"Vibration exceeded safe limits: {data['vibration']}G",
            "timestamp": timestamp
        })

    return alerts
