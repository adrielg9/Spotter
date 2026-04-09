import sqlite3
from datetime import datetime # <--- 1. IMPORTANTE: Agregamos esto

class CobrosRepository:
    def __init__(self, db_context):
        self.db = db_context

    def registrar_transaccion(self, dni, fecha_vencimiento, monto, concepto, metodo_pago, usuario):
        # 2. Generamos la fecha con hora exacta (YYYY-MM-DD HH:MM:SS)
        fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 3. Modificamos el SQL para insertar explícitamente 'fecha_pago'
        sql = """
        INSERT INTO cobros (dni, fecha_vencimiento, monto, concepto, metodo_pago, usuario, fecha_pago) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        conn = self.db.get_connection()
        # 4. Pasamos fecha_hora_actual al final
        conn.execute(sql, (dni, fecha_vencimiento, monto, concepto, metodo_pago, usuario, fecha_hora_actual))
        conn.commit()

    def obtener_ultimo_pago(self, dni):
        sql = "SELECT * FROM cobros WHERE dni = ? ORDER BY fecha_vencimiento DESC LIMIT 1"
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (dni,))
        row = cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "dni": row[1],
                "fecha_vencimiento": row[2],
                "monto": row[3],
                "concepto": row[4]
            }
        return None
    
    def obtener_vencimiento(self, dni):
        sql = "SELECT MAX(fecha_vencimiento) FROM cobros WHERE dni = ?"
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (dni,))
        row = cursor.fetchone()
        if row and row[0]:
            return row[0]
        return None

    def obtener_ultimo_concepto(self, dni):
        try:
            cursor = self.db.connection.cursor()
            query = """
                    SELECT concepto 
                    FROM cobros 
                    WHERE dni = ? 
                    ORDER BY id DESC 
                    LIMIT 1
                """
            cursor.execute(query, (dni,))
            row = cursor.fetchone()
            if row:
                return row["concepto"]
            return None
        except Exception as e:
            print(f"Error al obtener último concepto: {e}")
            return None

    def obtener_historial_completo(self):
        cursor = self.db.connection.cursor()
        query = """
            SELECT 
                c.id, 
                s.nombre as nombre_completo, 
                c.monto, 
                c.fecha_pago, 
                c.concepto,
                c.metodo_pago,
                c.usuario
            FROM cobros c
            JOIN socios s ON c.dni = s.dni
            ORDER BY c.id DESC
        """
        # Nota: Cambié el ORDER BY a c.id DESC para ver siempre lo último registrado arriba
        cursor.execute(query)
        columnas = [desc[0] for desc in cursor.description]
        return [dict(zip(columnas, row)) for row in cursor.fetchall()]
    
    # ... (código anterior) ...

    def eliminar_pago(self, id_pago):
        try:
            sql = "DELETE FROM cobros WHERE id = ?"
            conn = self.db.get_connection()
            conn.execute(sql, (id_pago,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error al eliminar pago: {e}")
            return False