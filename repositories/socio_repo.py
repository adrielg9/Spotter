import sqlite3

class SocioRepository:
    def __init__(self, db_context):
        self.db = db_context

    def crear(self, dni, nombre, telefono):

        sql = "INSERT INTO socios (dni, nombre, telefono, fecha_registro) VALUES (?, ?, ?, DATE('now'))"
        
        conn = self.db.get_connection()
        try:

            conn.execute(sql, (dni, nombre, telefono))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            raise ValueError(f"El socio con DNI {dni} ya existe.")

    def obtener_todos(self):
        # Traemos los datos básicos para el buscador y la lista
        sql = """
        SELECT s.dni, s.nombre, s.telefono, MAX(c.fecha_vencimiento) as vencimiento
        FROM socios s
        LEFT JOIN cobros c ON s.dni = c.dni
        GROUP BY s.dni, s.nombre, s.telefono
        ORDER BY s.nombre ASC
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        filas = cursor.fetchall()
        
        resultado = []
        for fila in filas:
            resultado.append({
                'dni': fila[0],
                'nombre': fila[1],
                'telefono': fila[2],
                'vencimiento': fila[3]
            })
        return resultado

    def obtener_por_dni(self, dni):
        # 1. Limpieza de datos (Blindaje)
        # Convertimos a string y quitamos espacios al principio y final
        dni_limpio = str(dni).strip()
          
        sql = "SELECT dni, nombre, telefono FROM socios WHERE dni = ?"
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Usamos el dni_limpio
        cursor.execute(sql, (dni_limpio,))
        row = cursor.fetchone()
        
        if row:
            return {'dni': row[0], 'nombre': row[1], 'telefono': row[2]}
            
        return None

    def actualizar(self, dni, nombre, telefono):
        sql = "UPDATE socios SET nombre = ?, telefono = ? WHERE dni = ?"
        conn = self.db.get_connection()
        cursor = conn.execute(sql, (nombre, telefono, dni))
        conn.commit()
        return cursor.rowcount > 0

    def eliminar(self, dni):
        sql = "DELETE FROM socios WHERE dni = ?"
        conn = self.db.get_connection()
        conn.execute(sql, (dni,))
        conn.commit()
    
    def obtener_nombres_y_dni(self):
        # Traemos DNI y Nombre para el buscador
        sql = "SELECT dni, nombre FROM socios ORDER BY nombre ASC"
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        return [{"dni": row[0], "nombre": row[1]} for row in cursor.fetchall()]
    
    # ... (dentro de la clase SocioRepo) ...
    
    