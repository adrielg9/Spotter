import flet as ft
from utils.logo import build_logo

class LoginView(ft.View):
    def __init__(self, page):
        super().__init__(route="/", scroll=ft.ScrollMode.AUTO)
        self.page = page
        self.controller = None 
        self.is_loading = False

        # --- PALETA DE COLORES ---
        self.colors = {
            "bg": "#09090B", 
            "card": "#09090B", 
            "border": "#27272A",
            "text": "#FFFFFF", 
            "muted": "#A1A1AA", 
            "blue": "#3B82F6",
            "purple": "#A855F7", 
            "input_bg": "#09090B", 
            "error": "#EF4444",
            "success": "#10B981"
        }

        self.logo_section = build_logo()
        self.login_card = ft.Container(padding=0) 

        self._dibujar_login_normal()

        self.bgcolor = self.colors["bg"]
        self.padding = 0 

        self.controls = [
            ft.Container(
                content=ft.Column(
                    controls=[self.logo_section, self.login_card],
                    spacing=0,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    width=480 # Ancho profesional
                ),
                expand=True,
                alignment=ft.alignment.center,
                padding=20,
            )
        ]

    def set_controller(self, controller):
        self.controller = controller

    # --- HELPERS DE UI ---

    def _crear_input(self, hint, icon, password=False, on_submit=None):
        return ft.TextField(
            hint_text=hint, 
            prefix_icon=icon, 
            password=password, 
            can_reveal_password=password,
            bgcolor=self.colors["input_bg"], 
            border_color=self.colors["border"],
            border_radius=8, 
            color="white", 
            focused_border_color=self.colors["blue"],
            on_submit=on_submit
        )

    def _crear_boton(self, text, on_click):
        return ft.Container(
            content=ft.Row([ft.Text(text, weight="bold", color="white", size=16)], alignment=ft.MainAxisAlignment.CENTER),
            gradient=ft.LinearGradient(colors=[self.colors["blue"], self.colors["purple"]]),
            border_radius=8, 
            padding=12, 
            alignment=ft.alignment.center,
            on_click=on_click, 
            ink=True,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.3, self.colors["blue"]))
        )

    def _get_error_container(self):
        if not hasattr(self, 'container_error'):
            self.container_error = ft.Container(
                content=ft.Text("", color=self.colors["error"], size=14, weight="bold"),
                bgcolor=ft.Colors.with_opacity(0.1, self.colors["error"]),
                border=ft.border.all(1, self.colors["error"]),
                border_radius=8, 
                padding=12, 
                visible=False
            )
        else:
            self.container_error.visible = False 
        return self.container_error

    def _render_view(self, title, subtitle, content_controls, show_back=True):
        header = ft.Container(
            content=ft.Column([
                ft.Text(title, size=24, weight="bold", color=self.colors["text"], text_align="center"),
                ft.Text(subtitle, size=14, color=self.colors["muted"], text_align="center"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
            alignment=ft.alignment.center, 
            margin=ft.margin.only(top=24 if show_back else 40, bottom=20)
        )

        inner_card = ft.Container(
            content=ft.Column(content_controls, spacing=15, horizontal_alignment=ft.CrossAxisAlignment.STRETCH),
            bgcolor=self.colors["card"], 
            border=ft.border.all(1, self.colors["border"]),
            border_radius=16, 
            padding=32,
            shadow=ft.BoxShadow(blur_radius=20, color=ft.Colors.with_opacity(0.1, "black"), offset=ft.Offset(0, 10))
        )

        elements = [header, inner_card]
        if show_back:
            btn_volver = ft.TextButton(
                content=ft.Row([
                    ft.Icon(ft.icons.ARROW_BACK, size=16, color=self.colors["muted"]),
                    ft.Text("Volver al inicio de sesión", color=self.colors["muted"])
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
                on_click=lambda _: self._dibujar_login_normal()
            )
            elements.extend([ft.Container(height=10), btn_volver])

        self.login_card.content = ft.Column(elements, spacing=0)
        self.update()

    # --- PANTALLAS ---

    def _dibujar_login_normal(self):
        self.txt_user = self._crear_input("Usuario", ft.icons.PERSON_OUTLINE, )
        self.txt_pass = self._crear_input("Contraseña", ft.icons.LOCK_OUTLINE, password=True)
        
        btn_login = self._crear_boton("Iniciar Sesión", lambda _: self.controller.ejecutar_login(self.txt_user.value, self.txt_pass.value))

        registro_footer = ft.Row([
            ft.Text("¿No tiene una cuenta?", color=self.colors["muted"], size=14),
            ft.TextButton("Registrarse", on_click=lambda _: self.controller.iniciar_registro())   
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=5)

        form = [
            ft.Text("Usuario", color=self.colors["text"]), self.txt_user,
            ft.Text("Contraseña", color=self.colors["text"]), self.txt_pass,
            self._get_error_container(),
            ft.Container(
                content=ft.Text("¿Olvidó su contraseña?", size=15, color=self.colors["blue"]), 
                alignment=ft.alignment.center_right, 
                on_click=lambda _: self.controller.iniciar_recuperacion()
            ),
            ft.Container(height=10), btn_login,
            ft.Container(height=10), registro_footer
        ]
        self._render_view("Bienvenido", "Ingrese sus credenciales para continuar", form, show_back=False)

    def dibujar_registro(self, lista_preguntas):
        self.reg_user = self._crear_input("Nombre de usuario", ft.icons.PERSON_ADD_OUTLINED)
        self.reg_dni = ft.TextField(
            hint_text="DNI (8 dígitos numéricos)", 
            prefix_icon=ft.icons.FINGERPRINT, 
            bgcolor=self.colors["input_bg"], 
            border_color=self.colors["border"],
            border_radius=8, 
            color="white", 
            focused_border_color=self.colors["blue"],
            max_length=8,
            keyboard_type=ft.KeyboardType.NUMBER,
            input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*$", replacement_string="")
        )
        self.reg_pass1 = self._crear_input("Contraseña", ft.icons.LOCK_OUTLINE, password=True)
        self.reg_pass2 = self._crear_input("Repita la contraseña", ft.icons.LOCK_RESET, password=True)
        self.reg_resp = self._crear_input("Respuesta secreta", ft.icons.QUESTION_ANSWER_OUTLINED)
        
        self.reg_preg = ft.Dropdown(
            label="Pregunta de Seguridad",
            options=[ft.dropdown.Option(p) for p in lista_preguntas],
            bgcolor=self.colors["input_bg"], border_color=self.colors["border"],
            border_radius=8, color="white"
        )

        btn = self._crear_boton("Crear Cuenta", lambda _: self.controller.ejecutar_registro_final(
            self.reg_user.value, self.reg_dni.value, self.reg_pass1.value, self.reg_pass2.value, 
            self.reg_preg.value, self.reg_resp.value
        ))

        form = [
            ft.Text("Usuario y DNI", size=14, weight="500", color=self.colors["text"]), self.reg_user, self.reg_dni,
            ft.Text("Seguridad", size=14, weight="500", color=self.colors["text"]), self.reg_pass1, self.reg_pass2,
            ft.Text("Recuperación", size=14, weight="500", color=self.colors["text"]), self.reg_preg, self.reg_resp,
            self._get_error_container(), btn
        ]
        self._render_view("Crear Perfil", "Complete los datos para registrarse", form)

    def dibujar_paso1_identificacion(self):
        """Nuevo Paso 1: Elegir DNI o Usuario"""
        self.drop_metodo = ft.Dropdown(
            label="Buscar por:",
            options=[ft.dropdown.Option("DNI"), ft.dropdown.Option("Usuario")],
            value="DNI", bgcolor=self.colors["input_bg"], border_color=self.colors["border"], color="white"
        )
        self.txt_valor_identidad = self._crear_input("Ingrese el dato...", ft.icons.SEARCH)
        
        btn = self._crear_boton("Continuar", lambda _: self.controller.validar_identificacion_recuperacion(
            self.drop_metodo.value, self.txt_valor_identidad.value
        ))
        
        form = [self.drop_metodo, self.txt_valor_identidad, self._get_error_container(), btn]
        self._render_view("Recuperar Acceso", "Seleccione cómo desea buscar su cuenta", form)

    def dibujar_paso3_respuesta(self, pregunta_texto):
        """Paso 2: Responder la pregunta que el sistema encontró"""
        self.txt_respuesta = self._crear_input("Su respuesta...", ft.icons.QUESTION_ANSWER)
        btn = self._crear_boton("Verificar", lambda _: self.controller.verificar_respuesta_final(self.txt_respuesta.value))
        
        form = [
            ft.Text(f"Pregunta: {pregunta_texto}", size=16, weight="bold", color=self.colors["blue"], text_align="center"),
            self.txt_respuesta, self._get_error_container(), btn
        ]
        self._render_view("Seguridad", "Responda para validar su identidad", form)

    def dibujar_paso4_nueva_clave(self):
        self.txt_new_pass1 = self._crear_input("Nueva Contraseña", ft.icons.LOCK_OUTLINE, password=True)
        self.txt_new_pass2 = self._crear_input("Repita la contraseña", ft.icons.LOCK_RESET, password=True)
        btn = self._crear_boton("Cambiar Contraseña", lambda _: self.controller.actualizar_contrasena_final(
            self.txt_new_pass1.value, self.txt_new_pass2.value
        ))
        form = [self.txt_new_pass1, self.txt_new_pass2, self._get_error_container(), btn]
        self._render_view("Restablecer", "Cree una nueva clave de acceso", form)

    def dibujar_paso5_exito(self):
        icon = ft.Icon(ft.icons.CHECK_CIRCLE_ROUNDED, color=self.colors["success"], size=80)
        btn_login = self._crear_boton("Ir al Login", lambda _: self._dibujar_login_normal())
        form = [icon, ft.Text("¡Contraseña actualizada!", size=18, weight="bold"), btn_login]
        self._render_view("Éxito", "Ya puede usar su nueva contraseña", form, show_back=False)

    def mostrar_snack(self, mensaje, color_verde=False):
        if not color_verde:
            self.container_error.content.value = mensaje
            self.container_error.visible = True
            self.update()

