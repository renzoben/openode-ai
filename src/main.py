from fastapi import FastAPI, HTTPException
import sqlite3

# 1. Instanciamos la API
app = FastAPI(
    title="opeNode.ai API",
    description="Backend para el monitoreo de telemetría industrial",
    version="1.0.0"
)

# Función para conectar a la DB
def get_db():
    conn = sqlite3.connect('openode.db')
    conn.row_factory = sqlite3.Row  # Esto permite acceder por nombre de columna
    return conn

# 2. Endpoint de Bienvenida (Health Check)
@app.get("/")
def home():
    return {
        "message": "Bienvenido a opeNode.ai API",
        "status": "online",
        "docs": "/docs"
    }

# 3. Endpoint para obtener telemetría
@app.get("/telemetry")
def get_telemetry(limit: int = 10):
    """Obtiene los últimos registros de telemetría de la base de datos."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Consulta SQL para los últimos N registros
        query = "SELECT * FROM telemetry ORDER BY id DESC LIMIT ?"
        cursor.execute(query, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        # Convertimos las filas a una lista de diccionarios (Formato JSON)
        result = [dict(row) for row in rows]
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# ... (mantén el código anterior igual) ...

@app.post("/maintenance/reset")
def reset_alerts():
    """Lógica de mantenimiento: resetea todos los estados CRITICAL a RESOLVED."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # 1. Verificamos si hay algo que resetear
        cursor.execute("SELECT COUNT(*) FROM telemetry WHERE status = 'CRITICAL'")
        count = cursor.fetchone()[0]
        
        if count == 0:
            return {"message": "No hay alertas críticas pendientes.", "cleared": 0}
            
        # 2. Ejecutamos el Update
        cursor.execute("UPDATE telemetry SET status = 'RESOLVED' WHERE status = 'CRITICAL'")
        conn.commit()
        conn.close()
        
        return {
            "message": "Sistema reseteado exitosamente.",
            "cleared_alerts": count,
            "status": "SISTEMA SALUDABLE"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))