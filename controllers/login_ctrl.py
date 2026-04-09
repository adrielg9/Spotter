from utils.audit_logger import AuditLogger

class LoginCtrl:
    def __init__(self, view, service):
        self.view = view
        self.service = service  # AuthService
        self.temp_user = None

    # --- 1. LÓGICA DE LOGIN ---
    def ejecutar_login(self, user, password):
        if not user or not password:
            return self.view.mostrar_snack("Por favor complete todos los campos")
        
        if self.service.login(user, password):
            self.view.page.session.set("user", user) 
            
            logger = AuditLogger()
            id_sesion = logger.registrar_ingreso(user)
            self.view.page.session.set("session_id", id_sesion)
            
            self.view.page.go("/home")
        else:
            self.view.mostrar_snack("Usuario o contraseña incorrectos")

    # --- 2. LÓGICA DE RECUPERACIÓN (DNI o Usuario) ---
    
    def iniciar_recuperacion(self):
        """Paso 1: Muestra la pantalla para elegir método de búsqueda"""
        self.temp_user = None
        self.view.dibujar_paso1_identificacion()

    def validar_identificacion_recuperacion(self, tipo, valor):
        """Paso 2: Valida la identidad según el método elegido (DNI o Usuario)"""
        if not valor:
            return self.view.mostrar_snack(f"Ingrese su {tipo}")

        # Buscamos el nombre de usuario usando el servicio unificado
        # (Asegúrate de haber agregado 'identificar_usuario_recuperacion' a tu AuthService)
        username = self.service.identificar_usuario_recuperacion(tipo, valor)
        
        if username:
            self.temp_user = username
            # Obtenemos la pregunta específica que el usuario configuró al registrarse
            pregunta_texto = self.service.obtener_pregunta_seguridad(username)
            # Pasamos directo a que responda su pregunta
            self.view.dibujar_paso3_respuesta(pregunta_texto)
        else:
            self.view.mostrar_snack(f"No se encontró ninguna cuenta con ese {tipo}")

    def verificar_respuesta_final(self, respuesta):
        """Valida la respuesta y permite pasar al cambio de contraseña"""
        if not respuesta:
            return self.view.mostrar_snack("Ingrese su respuesta")
        
        u = self.service.repo.obtener_por_usuario(self.temp_user)
        if not u:
            return self.view.mostrar_snack("Error: Usuario no encontrado")

        # CORRECCIÓN: Usamos u['columna'] en lugar de u.get(). 
        # Agregamos "or ''" por si el campo es NULL en la base de datos.
        real = str(u['respuesta_seguridad'] or '').lower().strip()
        ingresada = str(respuesta).lower().strip()

        if real == ingresada:
            self.view.dibujar_paso4_nueva_clave()
        else:
            self.view.mostrar_snack("Respuesta incorrecta")

    def actualizar_contrasena_final(self, clave1, clave2):
        """PASO 4: Valida y actualiza en la DB, luego muestra éxito"""
        if not clave1 or not clave2:
            return self.view.mostrar_snack("Complete ambos campos")
        
        if clave1 != clave2:
            return self.view.mostrar_snack("Las contraseñas no coinciden")
        
        if len(clave1) < 6:
            return self.view.mostrar_snack("La contraseña debe tener al menos 6 caracteres")

        u = self.service.repo.obtener_por_usuario(self.temp_user)
        
        # CORRECCIÓN: Acceso directo a la columna para sqlite3.Row
        resp_correcta = u['respuesta_seguridad']
        
        # Realiza el UPDATE en la tabla de usuarios
        if self.service.verificar_y_cambiar_clave(self.temp_user, resp_correcta, clave1):
            self.temp_user = None
            self.view.dibujar_paso5_exito() 
        else:
            self.view.mostrar_snack("Error al actualizar la contraseña")

    # --- 3. LÓGICA DE REGISTRO ---
    
    def iniciar_registro(self):
        """Muestra la vista de registro"""
        lista_preguntas = list(self.service.PREGUNTAS.values())
        self.view.dibujar_registro(lista_preguntas)

    def ejecutar_registro_final(self, user, dni, pass1, pass2, pregunta_txt, respuesta):
        """Procesa el registro del nuevo Staff incluyendo el DNI"""
        if not all([user, dni, pass1, pass2, pregunta_txt, respuesta]):
            return self.view.mostrar_snack("Por favor complete todos los campos")

        # --- VALIDACIÓN DE DNI ---
        if len(dni) != 8:
            self.view.mostrar_snack("El DNI debe tener exactamente 8 dígitos")
            self.view.reg_dni.focus()
            return
        # -------------------------
    
        if pass1 != pass2:
            return self.view.mostrar_snack("Las contraseñas no coinciden")
    
        if len(pass1) < 6:
            return self.view.mostrar_snack("La contraseña debe tener al menos 6 caracteres")

        # Buscamos el ID de la pregunta seleccionada
        pregunta_id = next((k for k, v in self.service.PREGUNTAS.items() if v == pregunta_txt), 4)

        # Enviamos los parámetros al servicio (incluyendo DNI)
        exito, msg = self.service.registrar_usuario(user, pass1, dni, pregunta_id, respuesta)
    
        if exito:
            self.view.mostrar_snack(msg, color_verde=True)
            self.view._dibujar_login_normal()
        else:
            self.view.mostrar_snack(msg)