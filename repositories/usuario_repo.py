import sqlite3

class UsuarioRepository:
    def __init__(self, db_context):
        self.db = db_context

    def obtener_por_usuario(self, username):
        """Busca un usuario por su nombre de cuenta"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE username = ?", (username,))
        # Como usamos row_factory = sqlite3.Row, podemos tratar el resultado como diccionario
        return cursor.fetchone()

    def obtener_por_dni(self, dni):
        """Busca un usuario por su DNI (útil para recuperación de staff)"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE dni = ?", (dni,))
        return cursor.fetchone()

    def crear_usuario(self, username, password, dni, pregunta_id, respuesta_seguridad, direccion=""):
        """Registra un nuevo usuario en el sistema"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO usuarios (username, password, dni, pregunta_id, respuesta_seguridad, direccion)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (username, password, dni, pregunta_id, respuesta_seguridad, direccion))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            print(f"Error: El usuario '{username}' ya existe.")
            return False
        except Exception as e:
            print(f"Error al crear usuario: {e}")
            return False

    def actualizar_password(self, username, nueva_password):
        """Actualiza la contraseña de un usuario específico"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE usuarios 
                SET password = ? 
                WHERE username = ?
            """, (nueva_password, username))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error al actualizar contraseña: {e}")
            return False

    def listar_usuarios(self):
        """Devuelve la lista de todo el staff registrado"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, dni, direccion FROM usuarios")
        return cursor.fetchall()