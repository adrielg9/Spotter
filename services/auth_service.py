class AuthService:
    # Definimos las constantes aquí para usarlas en todo el sistema
    PREGUNTAS = {
        1: "Equipo Favorito",
        2: "Direccion",
        3: "Año de inauguracion",
        4: "Hobbie Favorito"
    }

    def __init__(self, usuario_repo):
        self.repo = usuario_repo


    def login(self, user, password):
        u = self.repo.obtener_por_usuario(user)
        # Verificamos que exista y la contraseña coincida
        if u and u['password'] == password:
            return True
        return False

    def obtener_pregunta_seguridad(self, user):
        """Devuelve el TEXTO de la pregunta que eligió el usuario"""
        u = self.repo.obtener_por_usuario(user)
        if not u: 
            return None
        
        # CORRECCIÓN: sqlite3.Row no tiene .get(). Usamos acceso directo.
        # Si el valor es None en la DB, usamos la 4 por defecto.
        preg_id = u['pregunta_id'] if u['pregunta_id'] is not None else 4
        
        return self.PREGUNTAS.get(preg_id, "Pregunta de seguridad no configurada")

    def verificar_y_cambiar_clave(self, user, respuesta_ingresada, nueva_clave):
        """Verifica la respuesta y, si es correcta, cambia la clave"""
        u = self.repo.obtener_por_usuario(user)
        if not u: return False
        
        # CORRECCIÓN: Acceso directo a las columnas
        real = str(u['respuesta_seguridad'] or '').lower().strip()
        ingresada = str(respuesta_ingresada).lower().strip()
        
        if real == ingresada:
            self.repo.actualizar_password(user, nueva_clave)
            return True
            
        return False

    # --- ACTUALIZADO: REGISTRO CON DNI ---
    def registrar_usuario(self, username, password, dni, pregunta_id, respuesta):
        if self.repo.obtener_por_usuario(username):
            return False, "El nombre de usuario ya está en uso"
        
        try:
            # Enviamos el DNI al repositorio
            self.repo.crear_usuario(username, password, dni, pregunta_id, respuesta)
            return True, "Usuario creado con éxito"
        except Exception as e:
            return False, f"Error al crear usuario: {str(e)}"
    
    # --- BUSCAR POR IDENTIDAD (DNI o USER) ---
    def identificar_usuario_recuperacion(self, tipo, valor):
        """Busca al usuario según la elección: 'DNI' o 'Usuario'"""
        u = None
        if tipo == "DNI":
            u = self.repo.obtener_por_dni(valor)
        else:
            u = self.repo.obtener_por_usuario(valor)
            
        if u:
            return u['username'] # Siempre devolvemos el username para el siguiente paso
        return None