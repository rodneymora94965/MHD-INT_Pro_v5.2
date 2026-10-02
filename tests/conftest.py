"""
Configuración de pytest para MHD-INT.
"""
import sys
from pathlib import Path

# Agregar la raíz del proyecto al path para que los tests puedan importar los módulos
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
