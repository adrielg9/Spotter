import os
import sys

def obtener_ruta_db(nombre_db="gym.db"):
    """
    Devuelve la ruta absoluta de la base de datos.
    - Si es EXE: La busca al lado del ejecutable.
    - Si es Código: La busca en la raíz del proyecto.
    """
    if getattr(sys, 'frozen', False):
        # Estamos en modo ejecutable (.exe)
        base_path = os.path.dirname(sys.executable)
    else:
        # Estamos en modo desarrollo (código fuente)
        # subimos 2 niveles desde utils/path_handler.py hasta la raiz
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
    return os.path.join(base_path, nombre_db)

def obtener_ruta_recurso(ruta_relativa):
    """
    Usa esta función para IMÁGENES y SONIDOS que van DENTRO del exe.
    """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, ruta_relativa)
    return os.path.join(os.path.abspath("."), ruta_relativa)