from fastapi import FastAPI
from app.routes import devices, telemetry, alerts

app = FastAPI(
    title="IoT Streaming Platform API",
    description="API to query IoT device telemetry and alerts",
    version="1.0.0"
)

# Include routers
app.include_router(devices.router)
app.include_router(telemetry.router)
app.include_router(alerts.router)

@app.get("/")
def root():
    return {"message": "Welcome to IoT Streaming Platform API", "docs": "/docs"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
