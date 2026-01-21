import asyncio
import random
from datetime import datetime
from pydantic import BaseModel, Field, ValidationError

# 1. THE CONTRACT: Defining the Industrial Schema
# This ensures that no "poisoned" data enters our system.
class TelemetryData(BaseModel):
    #device_id: str = Field(..., example="S7-1200-NODE-01")
    device_id: str = Field(..., json_schema_extra={"example": "S7-1200-NODE-01"})
    temperature: float = Field(..., ge=-10.0, le=120.0)  # Celsius limits
    pressure: float = Field(..., ge=0.0, le=15.0)       # Bar limits
    status: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# 2. THE LOGIC: Simulating PLC Behavior
async def plc_node_simulator(node_id: str):
    """Simulates an industrial PLC generating telemetries."""
    print(f"[*] Starting node: {node_id}")
    
    while True:
        # Generate raw physical signals (with some random noise)
        raw_temp = round(random.uniform(20.0, 25.0) + random.uniform(-1, 1), 2)
        raw_press = round(random.uniform(2.0, 3.5), 2)
        
        try:
            # Validate the data using our Pydantic model
            reading = TelemetryData(
                device_id=node_id,
                temperature=raw_temp,
                pressure=raw_press,
                status="OPERATIONAL"
            )
            print(f"[VALID] {reading.timestamp} | {node_id} | Temp: {reading.temperature}°C | Press: {reading.pressure} bar")
            
        except ValidationError as e:
            # This is where we catch sensor failures or out-of-bounds signals
            print(f"[ERROR] Data validation failed for {node_id}: {e.json()}")

        # Simulation interval (e.g., every 2 seconds)
        await asyncio.sleep(2)

# 3. THE ORCHESTRATOR: Running multiple nodes
async def main():
    # We can scale this to simulate an entire factory floor
    nodes = ["S7-1200-LAB-01", "S7-1200-LAB-02", "ARDUINO-EDGE-01"]
    tasks = [plc_node_simulator(node) for node in nodes]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] Simulation stopped by user.")
