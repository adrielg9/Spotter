import json
import os
import uuid
import threading
from datetime import datetime

class AuditLogger:
    # --- CANDADO COMPARTIDO (Static) ---
    # Esto obliga a hacer fila para escribir en el archivo
    _lock = threading.Lock() 

    def __init__(self, archivo="historial_logins.json"):
        self.archivo = archivo

    def registrar_ingreso(self, username):
        session_id = str(uuid.uuid4())
        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        nuevo_registro = {
            "id": session_id,
            "usuario": username,
            "inicio": ahora,
            "ultimo_latido": ahora,
            "fin": None 
        }

        with AuditLogger._lock:
            datos = self._leer_datos_sin_lock()
            datos.insert(0, nuevo_registro)
            datos = datos[:500] 
            self._guardar_datos_sin_lock(datos)
        
        return session_id

    def registrar_salida(self, session_id):
        if not session_id: return
        
        with AuditLogger._lock:
            datos = self._leer_datos_sin_lock()
            for registro in datos:
                if registro.get("id") == session_id:
                    if registro["fin"] is None:
                        registro["fin"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    break
            self._guardar_datos_sin_lock(datos)

    def actualizar_latido(self, session_id):
        if not session_id: return
        
        # Intentamos obtener el candado, pero si está ocupado no insistimos mucho
        # para no bloquear el sistema por un simple latido.
        if AuditLogger._lock.acquire(blocking=False):
            try:
                datos = self._leer_datos_sin_lock()
                cambio = False
                ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                for registro in datos:
                    if registro.get("id") == session_id and registro["fin"] is None:
                        registro["ultimo_latido"] = ahora
                        cambio = True
                        break
                
                if cambio:
                    self._guardar_datos_sin_lock(datos)
            finally:
                AuditLogger._lock.release()

    def cerrar_sesiones_huerfanas(self):
        with AuditLogger._lock:
            datos = self._leer_datos_sin_lock()
            modificado = False
            
            for registro in datos:
                if registro.get("fin") is None:
                    ultimo_visto = registro.get("ultimo_latido") or registro.get("inicio")
                    registro["fin"] = ultimo_visto
                    modificado = True
            
            if modificado:
                self._guardar_datos_sin_lock(datos)
    
    def obtener_historial(self):
        with AuditLogger._lock:
            return self._leer_datos_sin_lock()

    # --- Métodos internos sin bloqueo ---
    def _leer_datos_sin_lock(self):
        if not os.path.exists(self.archivo): return []
        try:
            with open(self.archivo, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return []

    def _guardar_datos_sin_lock(self, datos):
        try:
            with open(self.archivo, "w", encoding="utf-8") as f:
                json.dump(datos, f, indent=4)
        except: pass