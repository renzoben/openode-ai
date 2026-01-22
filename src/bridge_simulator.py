import asyncio
import random
import logging
from datetime import datetime
from pydantic import BaseModel, Field, ValidationError

# Sprint 1 Configuration
FAILURE_PROBABILITY = 0.15  # Increased slightly to see the effect faster
CRITICAL_THRESHOLD = 3

# Configure anomaly logger
logging.basicConfig(
    filename='anomalies.log',
    level=logging.ERROR,
    format='%(asctime)s | %(levelname)s | %(message)s'
)

class TelemetryData(BaseModel):
    device_id: str = Field(..., json_schema_extra={"example": "S7-1200-NODE-01"})
    temperature: float = Field(..., ge=-10.0, le=120.0)
    pressure: float = Field(..., ge=0.0, le=15.0)
    status: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

def get_sensor_readings():
    temp = round(random.uniform(20.0, 25.0), 2)
    press = round(random.uniform(2.0, 3.5), 2)
    if random.random() < FAILURE_PROBABILITY:
        temp = 999.9  # Trigger validation error
    return temp, press

async def plc_node_simulator(node_id: str):
    """Simulates a PLC with intelligent failure tracking."""
    print(f"[*] Starting node: {node_id}")
    consecutive_failures = 0  # Local state for each node
    
    while True:
        raw_temp, raw_press = get_sensor_readings()
        
        try:
            reading = TelemetryData(
                device_id=node_id,
                temperature=raw_temp,
                pressure=raw_press,
                status="OPERATIONAL"
            )
            # Reset counter on successful validation
            consecutive_failures = 0
            print(f"[VALID] {node_id} | Temp: {reading.temperature}°C")
            
        except ValidationError as e:
            consecutive_failures += 1
            error_detail = e.errors()[0]
            field = error_detail['loc'][0]
            
            # Standard Alert
            print(f"\033[91m[ALERT]\033[0m {node_id} | Failure {consecutive_failures}/{CRITICAL_THRESHOLD} | {field}: {raw_temp}")
            
            # CRITICAL FAILURE LOGIC
            if consecutive_failures >= CRITICAL_THRESHOLD:
                print(f"\033[41m[CRITICAL SYSTEM FAILURE]\033[0m {node_id} HAS FAILED 3 TIMES. MAINTENANCE REQUIRED.")
                logging.critical(f"NODE_OFFLINE: {node_id} reached {consecutive_failures} consecutive failures.")

            logging.error(f"Node: {node_id} | Field: {field} | Value: {raw_temp}")

        await asyncio.sleep(2)

async def main():
    nodes = ["S7-1200-LAB-01", "S7-1200-LAB-02", "ARDUINO-EDGE-01"]
    tasks = [plc_node_simulator(node) for node in nodes]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] Simulation stopped by user.")