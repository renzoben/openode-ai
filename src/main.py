import os
import sqlite3
from fastapi import FastAPI, HTTPException
from src.core.orchestrator import SystemOrchestrator

# 1. Configuración de Rutas (Misma lógica que el simulador)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR)
DB_PATH = os.path.join(BASE_DIR, "openode.db")
CONFIG_PATH = os.path.join(BASE_DIR, "config", "nodes.json")

app = FastAPI(title="opeNode.ai - Gateway IIoT")

# 2. El "Recibidor" (Evita el 404 en la raíz)
@app.get("/")
def home():
    return {
        "project": "opeNode.ai",
        "status": "Online",
        "author": "Renzo",
        "endpoints": ["/telemetry", "/system/nodes", "/docs"]
    }

# 3. Endpoint de Telemetría
@app.get("/telemetry")
def get_telemetry(limit: int = 10):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM telemetry ORDER BY id DESC LIMIT ?", (limit,))
        data = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error DB: {e}")

# 4. Endpoint de Nodos (Para ver tus kits activos)
@app.get("/system/nodes")
def get_active_nodes():
    orch = SystemOrchestrator(config_path=CONFIG_PATH)
    orch.load_configuration()
    return {"active_nodes": orch.active_nodes}