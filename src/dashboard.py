import sqlite3
import time
import os
from datetime import datetime

def get_live_status():
    # Conectamos a la base de datos que está en la misma carpeta
    conn = sqlite3.connect('openode.db')
    cursor = conn.cursor()

    # Limpiar la pantalla para crear el efecto de monitor
    os.system('clear')

    print("=" * 65)
    print(f"      OPENODE.AI - LIVE INDUSTRIAL MONITOR")
    print(f"      Última actualización: {datetime.now().strftime('%H:%M:%S')}")
    print("      (Presiona Ctrl+C para salir)")
    print("=" * 65)

    # Encabezado de la tabla
    print(f"{'HORA':<15} | {'DISPOSITIVO':<18} | {'TEMP':<10} | {'ESTADO':<12}")
    print("-" * 65)
    
    # Consultamos los últimos 10 registros para ver lo más reciente
    cursor.execute("SELECT timestamp, device_id, temperature, status FROM telemetry ORDER BY id DESC LIMIT 10")
    
    for row in cursor.fetchall():
        # Limpiar la estampa de tiempo para mostrar solo la hora
        hora = row[0].split('T')[1][:8]
        device = row[1]
        temp = row[2]
        status = row[3]

        # Lógica de colores ANSI para alertas (Rojo si > 120°C)
        if temp > 120:
            temp_str = f"\033[91m{temp:>6}°C\033[0m" # Rojo
            status_str = f"\033[91m{status:<12}\033[0m"
        else:
            temp_str = f"{temp:>6}°C"
            status_str = status
        
        print(f"{hora:<15} | {device:<18} | {temp_str:<10} | {status_str:<12}")
    # --- RESUMEN DE SALUD ACTUALIZADO ---
    print("\n" + "=" * 65)
    print("      RESUMEN DE SALUD INDUSTRIAL (KPI)")
    
    # Buscamos específicamente registros con status 'CRITICAL'
    cursor.execute("""
        SELECT device_id, COUNT(*) 
        FROM telemetry 
        WHERE status = 'CRITICAL' 
        GROUP BY device_id
    """)
    
    anomalies = cursor.fetchall()
    if not anomalies:
        print("      ESTADO: \033[92mSISTEMA SALUDABLE - 0 FALLAS CRÍTICAS\033[0m")
    else:
        for node, count in anomalies:
            print(f"      \033[41m[CRITICAL]\033[0m {node:<18}: {count} FALLAS DE HARDWARE")
    print("=" * 65)
    conn.close()

if __name__ == "__main__":
    try:
        while True:
            get_live_status()
            time.sleep(3) # Frecuencia de muestreo del monitor
    except KeyboardInterrupt:
        print("\n[!] Dashboard cerrado por el usuario.")