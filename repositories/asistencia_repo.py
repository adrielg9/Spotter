import sqlite3
from datetime import datetime

class AsistenciaRepository:
    def __init__(self, db_context):
        self.db = db_context

    def registrar(self, dni):
        sql = "INSERT INTO asistencias (dni, fecha_hora) VALUES (?, ?)"
        
        # Obtenemos la fecha y hora actual
        ahora = datetime.now()
        
        conn = self.db.get_connection()
        conn.execute(sql, (dni, ahora))
        conn.commit()
        return True

    def obtener_historial(self, dni):
        # Método extra por si quieres ver el historial de alguien después
        sql = "SELECT fecha_hora FROM asistencias WHERE dni = ? ORDER BY fecha_hora DESC"
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (dni,))
        filas = cursor.fetchall()
        
        # Devolvemos una lista simple de fechas
        return [fila[0] for fila in filas]
    
    # ... (dentro de la clase AsistenciaRepo) ...

    def contar_asistencias_hoy(self):
        cursor = self.db.connection.cursor()
        # Compara la fecha de hoy con la fecha de ingreso
        sql = """
            SELECT COUNT(*) FROM asistencias 
            WHERE date(fecha_hora) = date('now', 'localtime')
        """
        cursor.execute(sql)
        return cursor.fetchone()[0]
    
    def contar_hoy(self, dni):
        """Cuenta las asistencias de un DNI en la fecha actual"""
        from datetime import datetime
        
        # Fecha de hoy formato YYYY-MM-DD
        hoy_str = datetime.now().strftime("%Y-%m-%d")
        
        # --- CORRECCIÓN AQUÍ: Usamos 'fecha_hora' en lugar de 'fecha' ---
        sql = "SELECT COUNT(*) FROM asistencias WHERE dni = ? AND fecha_hora LIKE ?"
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # El % es el comodín para la hora
        cursor.execute(sql, (dni, f"{hoy_str}%"))
        cantidad = cursor.fetchone()[0]
        
        return cantidad