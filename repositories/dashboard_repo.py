import sqlite3

class DashboardRepository:
    def __init__(self, db_context):
        self.db = db_context

    def obtener_resumen_dashboard(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        datos = {
            "socios_total": 0, "socios_al_dia": 0, "socios_deuda": 0,
            "asistencias_hoy": 0, "ingresos_mes": 0, "altas_mes": 0,
            "ultimos_pagos": [], "ultimas_asistencias": []
        }
        
        try:
            # --- 1. KPIs DE SOCIOS ---
            
            # Total Socios
            cursor.execute("SELECT COUNT(*) FROM socios")
            datos["socios_total"] = cursor.fetchone()[0]

            # Socios Al Día (Mirando tabla COBROS)
            cursor.execute("""
                SELECT COUNT(DISTINCT dni) FROM cobros 
                WHERE fecha_vencimiento >= DATE('now')
            """)
            datos["socios_al_dia"] = cursor.fetchone()[0]

            # Socios con Deuda
            datos["socios_deuda"] = datos["socios_total"] - datos["socios_al_dia"]
            if datos["socios_deuda"] < 0: datos["socios_deuda"] = 0

            # --- 2. KPIs DE ACTIVIDAD Y DINERO ---
            
            # Asistencias de hoy (CORREGIDO: usa 'fecha_hora')
            cursor.execute("SELECT COUNT(*) FROM asistencias WHERE date(fecha_hora) = DATE('now', 'localtime')")
            datos["asistencias_hoy"] = cursor.fetchone()[0]

            # Ingresos del Mes (Tabla COBROS)
            cursor.execute("""
                SELECT SUM(monto) FROM cobros 
                WHERE strftime('%Y-%m', fecha_pago) = strftime('%Y-%m', 'now')
            """)
            res_ingresos = cursor.fetchone()[0]
            datos["ingresos_mes"] = res_ingresos if res_ingresos else 0

            # Altas del Mes

            try:
                cursor.execute("SELECT COUNT(*) FROM socios WHERE strftime('%Y-%m', fecha_registro) = strftime('%Y-%m', 'now')")
                datos["altas_mes"] = cursor.fetchone()[0]
            except:
                datos["altas_mes"] = 0

            # --- 3. LISTAS (TABLAS) ---
            
            # Últimos 5 Pagos
            cursor.execute("""
                SELECT s.nombre, c.monto, c.fecha_vencimiento
                FROM cobros c 
                JOIN socios s ON c.dni = s.dni
                ORDER BY c.fecha_pago DESC 
                LIMIT 8
            """)
            
            pagos_raw = cursor.fetchall()
            for row in pagos_raw:
                venc_str = str(row[2]) if row[2] else "-"
                datos["ultimos_pagos"].append({
                    "nombre": str(row[0]),
                    "monto": row[1],
                    "fecha_vencimiento": venc_str
                })

            # Últimas 5 Asistencias (CORREGIDO: usa 'fecha_hora')
            # Nota: Hacemos JOIN por DNI, ya que confirmamos que 'dni' existe en ambas tablas
            try:
                cursor.execute("""
                    SELECT s.nombre, a.fecha_hora 
                    FROM asistencias a 
                    JOIN socios s ON a.dni = s.dni
                    ORDER BY a.fecha_hora DESC 
                    LIMIT 8
                """)
            except:
                # Fallback por seguridad si el JOIN falla
                cursor.execute("SELECT 'Socio', fecha_hora FROM asistencias ORDER BY fecha_hora DESC LIMIT 5")

            asistencias_raw = cursor.fetchall()
            for row in asistencias_raw:
                datos["ultimas_asistencias"].append({
                    "nombre": str(row[0]),
                    "hora": str(row[1]) # Enviamos la fecha_hora cruda a la vista
                })

        except Exception as e:
            print(f"❌ Error en DashboardRepository: {e}")
            # Retornamos los datos vacíos (ceros) si algo falla para no romper la app
            return datos
            
        return datos