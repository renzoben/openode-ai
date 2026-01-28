import json
import os

class SystemOrchestrator:
    def __init__(self, config_path='config/nodes.json'):
        self.config_path = config_path
        self.active_nodes = []

    def load_configuration(self):
        """Lee el archivo JSON y carga la lista de nodos."""
        if not os.path.exists(self.config_path):
            print(f"❌ Error: No se encontró el archivo {self.config_path}")
            return False
            
        with open(self.config_path, 'r') as f:
            config = json.load(f)
            print(f"📡 Sistema: {config['system_metadata']['location']} listo.")
            
            for node in config['modules']:
                if node['active']:
                    print(f"✅ Cargando módulo: [{node['type']}] - {node['id']}")
                    self.active_nodes.append(node)
                else:
                    print(f"💤 Módulo desactivado: {node['id']} (Saltando...)")
        return True

    def get_active_drivers(self):
        """Devuelve la lista de drivers que deben inicializarse."""
        return [node['driver'] for node in self.active_nodes]

# Prueba rápida de funcionamiento
if __name__ == "__main__":
    orchestrator = SystemOrchestrator()
    orchestrator.load_configuration()