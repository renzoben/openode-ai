import sqlite3
from datetime import datetime

def perform_maintenance():
    conn = sqlite3.connect('openode.db')
    cursor = conn.cursor()

    # 1. Verificamos si hay fallas antes de actuar
    cursor.execute("SELECT COUNT(*) FROM telemetry WHERE status = 'CRITICAL'")
    count = cursor.fetchone()[0]

    if count == 0:
        print("\n[i] No hay fallas críticas pendientes en el sistema.")
    else:
        print(f"\n[!] Detectadas {count} fallas críticas.")
        confirm = input("¿Confirmar mantenimiento realizado? (s/n): ")
        
        if confirm.lower() == 's':
            # 2. Actualizamos el estado de CRITICAL a RESOLVED
            timestamp = datetime.utcnow().isoformat()
            cursor.execute("""
                UPDATE telemetry 
                SET status = 'RESOLVED' 
                WHERE status = 'CRITICAL'
            """)
            conn.commit()
            print(f"\n\033[92m[SUCCESS]\033[0m Sistema reseteado. Alertas marcadas como RESUELTAS.")
        else:
            print("\n[!] Operación cancelada.")

    conn.close()

if __name__ == "__main__":
    perform_maintenance()