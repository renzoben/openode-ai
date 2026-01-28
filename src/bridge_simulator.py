import asyncio
import random
import sqlite3
import os
from datetime import datetime
from core.orchestrator import SystemOrchestrator

# 1. CONFIGURACIÓN DE RUTAS ABSOLUTAS (Para evitar archivos "fantasma")
# Detecta la carpeta 'src', luego sube un nivel a la raíz 'openode-ai'
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR)
DB_PATH = os.path.join(BASE_DIR, "openode.db")
CONFIG_PATH = os.path.join(BASE_DIR, "config", "nodes.json")

print(f"🔍 DIAGNÓSTICO DE RUTA:")
print(f"   > Buscando DB en: {DB_PATH}")
print(f"   > Buscando Config en: {CONFIG_PATH}\n")

def get_db_connection():
    return sqlite3.connect(DB_PATH)

# 2. FUNCIÓN DE INFRAESTRUCTURA (Fuerza la creación de la tabla)
def asegurar_tabla():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS telemetry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                value REAL NOT NULL,
                status TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()
        print("✅ INFRAESTRUCTURA: Tabla 'telemetry' verificada/creada con éxito.")
    except Exception as e:
        print(f"❌ ERROR CRÍTICO AL CREAR TABLA: {e}")
        exit(1) # Si no podemos crear la tabla, no tiene sentido seguir

async def simulate_device(node):
    node_id = node['id']
    node_type = node['type']
    
    while True:
        value = round(random.uniform(20.0, 80.0), 2)
        status = "OPERATIONAL"
        if random.random() < 0.05:
            status = "CRITICAL"
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO telemetry (device_id, value, status, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (node_id, value, status, datetime.now().isoformat()))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"❌ Error de persistencia en {node_id}: {e}")

        await asyncio.sleep(3)

async def main():
    # EJECUTAR PRIMERO LA CREACIÓN DE TABLA
    asegurar_tabla()

    # LUEGO CARGAR EL ORQUESTADOR
    orchestrator = SystemOrchestrator(config_path=CONFIG_PATH)
    if not orchestrator.load_configuration():
        print("❌ Falló la carga de configuración. Abortando.")
        return

    tasks = []
    for node in orchestrator.active_nodes:
        tasks.append(simulate_device(node))
    
    if not tasks:
        print("⚠️ Sistema en Standby: No hay nodos activos en el JSON.")
        return

    print(f"\n🚀 SIMULACIÓN INICIADA: Corriendo {len(tasks)} hilos industriales...")
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Simulación detenida.")