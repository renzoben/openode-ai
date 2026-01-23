import asyncio
import random
import sqlite3
from datetime import datetime
from pydantic import BaseModel, Field, ValidationError

# Configuración del Sistema
FAILURE_PROBABILITY = 0.15 
CRITICAL_THRESHOLD = 3

def init_db():
    conn = sqlite3.connect('openode.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS telemetry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            device_id TEXT,
            temperature REAL,
            pressure REAL,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_to_db(node_id, temp, press, status):
    """Función unificada para guardar datos válidos y críticos."""
    try:
        conn = sqlite3.connect('openode.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO telemetry (timestamp, device_id, temperature, pressure, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (datetime.utcnow().isoformat(), node_id, temp, press, status))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error en DB: {e}")

class TelemetryData(BaseModel):
    device_id: str
    temperature: float = Field(..., ge=-10.0, le=120.0)
    pressure: float = Field(..., ge=0.0, le=15.0)
    status: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

def get_sensor_readings():
    temp = round(random.uniform(20.0, 25.0), 2)
    press = round(random.uniform(2.0, 3.5), 2)
    if random.random() < FAILURE_PROBABILITY:
        temp = 999.9  
    return temp, press

async def plc_node_simulator(node_id: str):
    print(f"[*] Starting node: {node_id}")
    consecutive_failures = 0 
    
    while True:
        raw_temp, raw_press = get_sensor_readings()
        
        try:
            # Validación con Pydantic
            reading = TelemetryData(
                device_id=node_id, temperature=raw_temp, 
                pressure=raw_press, status="OPERATIONAL"
            )
            consecutive_failures = 0
            save_to_db(node_id, reading.temperature, reading.pressure, "OPERATIONAL")
            print(f"[VALID] {node_id} | Temp: {reading.temperature}°C | Data saved to DB.")
            
        except ValidationError:
            consecutive_failures += 1
            print(f"\033[91m[ALERT]\033[0m {node_id} | Failure {consecutive_failures}/{CRITICAL_THRESHOLD} | Temp: {raw_temp}")
            
            if consecutive_failures >= CRITICAL_THRESHOLD:
                print(f"\033[41m[CRITICAL SYSTEM FAILURE]\033[0m {node_id} NEEDS MAINTENANCE.")
                # Registramos el estado crítico en la DB en lugar de un archivo log
                save_to_db(node_id, raw_temp, raw_press, "CRITICAL")

        await asyncio.sleep(2)

async def main():
    nodes = ["S7-1200-LAB-01", "S7-1200-LAB-02", "ARDUINO-EDGE-01"]
    tasks = [plc_node_simulator(node) for node in nodes]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    init_db()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] Simulation stopped.")