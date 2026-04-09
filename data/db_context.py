import sqlite3
from utils.path_handler import obtener_ruta_db

class DatabaseContext:
    def __init__(self, db_name="gym.db"):
        self.db_name = obtener_ruta_db(db_name) 
        self._conn = None
        self.initialize_db()

    @property
    def connection(self):
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_name, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row 
        return self._conn

    def get_connection(self):
        return self.connection

    def initialize_db(self):
        cursor = self.connection.cursor()
        
        # 1. Tabla SOCIOS
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS socios (
            dni TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            telefono TEXT
        )
        """)
        
        # 2. Tabla COBROS 
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cobros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dni TEXT,
            fecha_vencimiento TEXT,
            monto REAL,
            concepto TEXT,
            fecha_pago TEXT DEFAULT CURRENT_DATE,
            metodo_pago TEXT, 
            usuario TEXT,
            FOREIGN KEY(dni) REFERENCES socios(dni)
        )
        """)
        
        # 3. Tabla ASISTENCIAS
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS asistencias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dni TEXT,
            fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(dni) REFERENCES socios(dni)
        )
        """)

        # 4. Tabla USUARIOS (DNI agregado al CREATE inicial)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            dni TEXT,            -- <--- NUEVO CAMPO: 
            direccion TEXT,
            pregunta_id INTEGER DEFAULT 4,
            respuesta_seguridad TEXT
        )""")
        
        # Admin por defecto (puedes asignarle un DNI manual aquí si quieres)
        cursor.execute("SELECT count(*) FROM usuarios WHERE username = 'admin'")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
            INSERT INTO usuarios (username, password, dni, direccion, pregunta_id, respuesta_seguridad)
            VALUES ('admin', '1234', '0000', 'Calle Falsa 123', 1, 'boca')
            """)
            print("✅ Admin creado.")
            
        # ---------------------------------------------------------
        # 5. ACTUALIZACIONES AUTOMÁTICAS (MIGRACIONES)
        # ---------------------------------------------------------
        
        # A) Migración: Metodo de Pago
        try:
            cursor.execute("ALTER TABLE cobros ADD COLUMN metodo_pago TEXT")
            print("✅ MIGRACIÓN: Columna 'metodo_pago' agregada.")
        except Exception:
            pass 


        # B) Migración: Usuario Responsable en cobros
        try:
            cursor.execute("ALTER TABLE cobros ADD COLUMN usuario TEXT")
        except Exception:
            pass

        # C) Migración: DNI en la tabla USUARIOS (NUEVO)
        # Esto asegura que tu base de datos actual reciba la columna sin borrarse
        try:
            cursor.execute("ALTER TABLE usuarios ADD COLUMN dni TEXT")
            print("✅ MIGRACIÓN: Columna 'dni' agregada a la tabla usuarios.")
        except Exception:
            pass # Ya existe o no se pudo agregar

        # ... (debajo de la Migración C que ya tienes) ...

        # D) MIGRACIÓN: Fecha de Registro en Socios (FALTABA ESTO)
        try:
            cursor.execute("ALTER TABLE socios ADD COLUMN fecha_registro TEXT DEFAULT CURRENT_DATE")
            print("✅ MIGRACIÓN: Columna 'fecha_registro' agregada a socios.")
        except Exception:
            pass # Si ya existe, salta aquí y no imprime nada (eso es normal)
            
   

        # ---------------------------------------------------------

        self.connection.commit()

    def cerrar(self):
        if self._conn:
            self._conn.close()
            self._conn = None