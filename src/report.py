import sqlite3
from datetime import datetime
import csv
import os

def generate_system_report():
    """Genera un resumen visual en la terminal."""
    conn = sqlite3.connect('openode.db')
    cursor = conn.cursor()

    print("=" * 50)
    print(f"      OPENODE.AI - INDUSTRIAL STATUS REPORT")
    print(f"      Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    # 1. MÉTRICAS GLOBALES
    cursor.execute("SELECT COUNT(*) FROM telemetry")
    total_records = cursor.fetchone()[0]
    
    cursor.execute("SELECT AVG(temperature) FROM telemetry WHERE temperature < 500")
    avg_temp = cursor.fetchone()[0] or 0 

    print(f"[*] Total Telemetries in DB: {total_records}")
    print(f"[*] Global Avg Temperature: {round(avg_temp, 2)}°C (Excl. Anomalies)")
    print("-" * 50)

    # 2. ANÁLISIS POR NODO (KPIs)
    print(f"{'DEVICE ID':<20} | {'COUNT':<6} | {'MAX T':<8} | {'MIN T':<8}")
    print("-" * 50)
    
    cursor.execute("""
        SELECT device_id, COUNT(*), MAX(temperature), MIN(temperature)
        FROM telemetry
        WHERE temperature < 500
        GROUP BY device_id
    """)
    
    for row in cursor.fetchall():
        print(f"{row[0]:<20} | {row[1]:<6} | {row[2]:<8.2f} | {row[3]:<8.2f}")

    # 3. REPORTE DE INCIDENCIAS
    print("-" * 50)
    print("[!] ANOMALY LOG SUMMARY")
    cursor.execute("SELECT device_id, COUNT(*) FROM telemetry WHERE temperature > 500 GROUP BY device_id")
    
    anomalies = cursor.fetchall()
    if not anomalies:
        print("    No critical anomalies detected in database.")
    else:
        for node, count in anomalies:
            print(f"    ALERT: {node} reported {count} out-of-bounds events (999.9°C)")

    conn.close()
    print("=" * 50)

def export_to_csv():
    """Exporta los datos a la carpeta /reports en la raíz del proyecto."""
    # 1. Lógica de rutas para encontrar la carpeta /reports
    base_dir = os.path.dirname(os.path.abspath(__file__)) # Ubicación de este script (src/)
    project_root = os.path.dirname(base_dir)             # Raíz (openode-ai/)
    folder = os.path.join(project_root, "reports")
    
    # Crear la carpeta si no existe
    os.makedirs(folder, exist_ok=True)
    
    filepath = os.path.join(folder, "telemetry_report.csv")

    # 2. Conexión y extracción de datos
    conn = sqlite3.connect('openode.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM telemetry")
    rows = cursor.fetchall()
    
    # Obtener nombres de columnas
    column_names = [description[0] for description in cursor.description]
    
    # 3. Escritura física del archivo
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(column_names)
        writer.writerows(rows)
        
    conn.close()
    print(f"\n[SUCCESS] Data exported to {filepath}")

if __name__ == "__main__":
    generate_system_report()
    export_to_csv()