import flet as ft
from utils.logo import build_logo

class CheckInView(ft.View):
    def __init__(self, page):
        super().__init__(route="/checkin")
        self.page = page
        self.controller = None

        # --- AUDIOS ---
        self.audio_exito = ft.Audio(src="sounds/success.mp3", autoplay=False)
        self.audio_vencido = ft.Audio(src="sounds/expired.mp3", autoplay=False)
        self.audio_no_existe = ft.Audio(src="sounds/not_found.mp3", autoplay=False)
        self.audio_ya_asistio = ft.Audio(src="sounds/repeat.mp3", autoplay=False)
        
        self.page.overlay.extend([
            self.audio_exito, self.audio_vencido, 
            self.audio_no_existe, self.audio_ya_asistio
        ])
                
        # --- COLORES ---
        self.c_bg = "#0a0a0a"          
        self.c_card = "#18181b"        
        self.c_blue_text = "#60a5fa"   
        self.c_muted = "#a1a1aa"       
        self.c_green = "#22c55e"       
        self.c_red = "#ef4444"         
        self.c_yellow = "#eab308"      
        self.c_orange = "#f97316" # Color para 'Ya asistió'
        self.c_border_blue = "#3b82f6"

        self.ancho_fijo_contenido = 500

        self.bgcolor = self.c_bg
        self.padding = 30
        self.scroll = ft.ScrollMode.AUTO
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.on_keyboard_event = self._on_keyboard_event

        # --- CONTROLES ---
        self.txt_dni = ft.Text(
            value="________", size=50, font_family="monospace", 
            weight=ft.FontWeight.BOLD, color=self.c_blue_text, text_align="center"
        )
        
        # Estado de espera (Reloj)
        self.estado_espera = ft.Column([
            ft.Icon(ft.icons.ACCESS_TIME_ROUNDED, size=60, color=self.c_muted),
            ft.Text("Esperando verificación...", color=self.c_muted, size=16)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10)

        self.contenedor_resultados = ft.Column(
            controls=[self.estado_espera],
            expand=True, 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
            alignment=ft.MainAxisAlignment.CENTER
        ) 
        
        self.instrucciones = ft.Text(
            "👉 Ingrese su DNI usando el teclado numérico", 
            color=self.c_muted, size=14, text_align="center"
        )

        self._build_ui()

    def set_controller(self, controller):
        self.controller = controller

    # --- CORRECCIÓN CLAVE PARA EL TECLADO ---
    def _on_keyboard_event(self, e: ft.KeyboardEvent):
        if not self.page or self.page.route != "/checkin": return
        if self.page.dialog and self.page.dialog.open: return

        key = e.key
        
        if "Numpad" in key and key[-1].isdigit():
            key = key[-1]

        # Ahora procesamos la tecla limpia
        if key.isdigit(): 
            self.controller.manejar_teclado(key)
        elif key == "Backspace": 
            self.controller.manejar_teclado("⌫")
        elif key in ["Enter", "Numpad Enter"]: 
            self.controller.verificar_dni()
        elif key in ["Escape", "Delete"]: 
            self.controller.manejar_teclado("Limpiar")

    def _build_ui(self):
        # 1. HEADER (Estilo original: Logo izq, Titulo centro, Admin der)
        logo_section = build_logo()

        header_titulo = ft.Column([
            ft.Text("Control de Asistencia", size=24, weight=ft.FontWeight.BOLD, color=self.c_blue_text),
            ft.Text("Bienvenido, identifíquese para ingresar", size=14, color=self.c_muted),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2)

        btn_admin = ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.SETTINGS, size=16, color=self.c_blue_text),
                ft.Text("ADMINISTRACIÓN", size=13, weight="bold", color=self.c_blue_text)
            ], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
            padding=ft.padding.symmetric(horizontal=8, vertical=8),
            border=ft.border.all(1, self.c_blue_text),
            border_radius=8,
            on_click=lambda _: self.page.go("/home"),
            on_hover=self._on_hover_admin,
        )

        top_bar = ft.Row(
            controls=[
                ft.Container(logo_section, expand=1, alignment=ft.alignment.center_left),
                ft.Container(header_titulo, expand=2, alignment=ft.alignment.center),
                ft.Container(btn_admin, expand=1, alignment=ft.alignment.center_right),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

        # 2. BOTÓN VERIFICAR
        self.btn_verificar = ft.Container(
            content=ft.Text("✓ VERIFICAR INGRESO", size=16, weight="bold", color="white"),
            gradient=ft.LinearGradient(colors=["#3b82f6", "#a855f7"]),
            border_radius=10, padding=15, width=self.ancho_fijo_contenido,
            alignment=ft.alignment.center,
            on_click=lambda _: self.controller.verificar_dni(),
            opacity=0.5, disabled=True
        )

        # 3. TARJETA IZQUIERDA (TECLADO - Estructura Original)
        card_izquierda = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=self.txt_dni,
                    bgcolor=ft.Colors.with_opacity(0.1, "#3b82f6"),
                    border=ft.border.all(1, ft.Colors.with_opacity(0.3, "#3b82f6")),
                    border_radius=12, padding=15, width=self.ancho_fijo_contenido, alignment=ft.alignment.center
                ),
                ft.Container(content=self._build_keypad(), alignment=ft.alignment.center),
                self.btn_verificar,
                ft.Container(content=self.instrucciones, width=self.ancho_fijo_contenido, alignment=ft.alignment.center)
            ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=self.c_card,
            border=ft.border.all(2, self.c_border_blue),
            border_radius=16, padding=30, height=650, col={"sm": 12, "md": 6}
        )

        # 4. TARJETA DERECHA (RESULTADOS - Estructura Original, Contenido Minimalista)
        card_derecha = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Text("RESULTADO", size=14, weight="bold", color=self.c_muted),
                    alignment=ft.alignment.center
                ),
                ft.Container(
                    content=self.contenedor_resultados,
                    expand=True,
                    alignment=ft.alignment.center
                )
            ], spacing=10),
            bgcolor=self.c_card,
            border=ft.border.all(2, self.c_border_blue),
            border_radius=16, padding=30, height=650, col={"sm": 12, "md": 6}
        )

        # ARMADO
        self.controls = [
            top_bar,
            ft.Divider(height=1, color=ft.Colors.GREY_900),
            ft.Container(height=15),
            ft.ResponsiveRow([card_izquierda, card_derecha], spacing=20)
        ]

    # --- RESULTADOS MINIMALISTAS ---
    # Aquí es donde ocurre la magia del diseño limpio que pediste

    def _build_result_success(self, data):
        """Muestra: Icono Verde, Nombre, 'Acceso Autorizado', aviso de vencimiento y actividad"""
        nombre = data.get('nombre', 'Socio').upper()
        actividad = data.get('cuota', '') 
        dias = data.get('dias', 0)
        
        content = [
            ft.Icon(ft.icons.CHECK_CIRCLE_OUTLINE_ROUNDED, size=90, color=self.c_green),
            ft.Container(height=10),
            ft.Text(nombre, size=26, weight="bold", color="white", text_align="center", max_lines=2),
            ft.Text("ACCESO AUTORIZADO", size=18, weight="bold", color=self.c_green),
        ]
        
        # --- CORRECCIÓN: Usamos Container para el margen ---
        if 0 <= dias <= 7:
            texto_vence = "⚠️ Su Cuota Vence en una semana" if dias == 7 else f"⚠️ Vence en {dias} días"
            if dias == 0: texto_vence = "⚠️ Su Cuota Vence HOY"
            if dias == 1: texto_vence = "⚠️ Su Cuota Vence MAÑANA"

            content.append(
                ft.Container( # <--- ENVOLTORIO NUEVO
                    content=ft.Text(texto_vence, size=20, color=self.c_yellow, weight="bold"),
                    margin=ft.margin.only(top=5) # El margen va AQUÍ, no en el Text
                )
            )
        
        if actividad:
            content.append(
                ft.Container(
                    content=ft.Text(actividad.upper(), size=12, color=self.c_green, weight="bold"),
                    bgcolor=ft.Colors.with_opacity(0.1, self.c_green),
                    padding=ft.padding.symmetric(horizontal=12, vertical=6),
                    border_radius=15,
                    margin=ft.margin.only(top=10)
                )
            )

        return ft.Container(
            content=ft.Column(content, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5, alignment=ft.MainAxisAlignment.CENTER),
            bgcolor=ft.Colors.with_opacity(0.05, self.c_green),
            border=ft.border.all(2, self.c_green),
            border_radius=20,
            padding=40,
            alignment=ft.alignment.center,
            margin=ft.margin.symmetric(horizontal=20),
            shadow=ft.BoxShadow(
                blur_radius=20,
                color=ft.Colors.with_opacity(0.2, self.c_green),
                spread_radius=0,
                offset=ft.Offset(0, 0)
            )
        )

    def _build_result_error(self, data):
        """Maneja Deuda (Rojo) o Repetición (Naranja)"""
        mensaje = data.get('mensaje_error', 'Acceso Denegado')
        nombre = data.get('nombre', 'Socio').upper()
        
        # Detectamos si es porque ya vino hoy para cambiar el color
        es_repeticion = "hoy" in mensaje.lower() or "registró" in mensaje.lower()
        color = self.c_orange if es_repeticion else self.c_red
        icono = ft.icons.HISTORY_TOGGLE_OFF if es_repeticion else ft.icons.CANCEL_OUTLINED
        texto_pie = "Vuelva mañana" if es_repeticion else "Consulte en recepción"

        return ft.Container(
            content=ft.Column([
                ft.Icon(icono, size=90, color=color),
                ft.Container(height=10),
                ft.Text(nombre, size=26, weight="bold", color="white", text_align="center", max_lines=2),
                ft.Text(mensaje, size=18, weight="bold", color=color, text_align="center"),
                ft.Text(texto_pie, color=self.c_muted, size=14)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5, alignment=ft.MainAxisAlignment.CENTER),
            
            # --- ESTILO PROFESIONAL ---
            bgcolor=ft.Colors.with_opacity(0.05, color),
            border=ft.border.all(2, color),
            border_radius=20,
            padding=40,
            alignment=ft.alignment.center,
            margin=ft.margin.symmetric(horizontal=20),
            # Sombreado "Glow" del color del error (Rojo o Naranja)
            shadow=ft.BoxShadow(
                blur_radius=20,
                color=ft.Colors.with_opacity(0.2, color),
                spread_radius=0,
                offset=ft.Offset(0, 0)
            )
        )

    def _build_result_not_found(self, dni):
        """Muestra: Icono Amarillo, 'No Encontrado', DNI"""
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.icons.PERSON_OFF_OUTLINED, size=90, color=self.c_yellow),
                ft.Container(height=10),
                ft.Text("SOCIO NO REGISTRADO", size=26, weight="bold", color=self.c_yellow, text_align="center"),
                ft.Text(f"DNI {dni}", size=18, color="white", weight="bold"),
                ft.Text("Por favor, regístrese", color=self.c_muted, size=14)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5, alignment=ft.MainAxisAlignment.CENTER),

            # --- ESTILO PROFESIONAL ---
            bgcolor=ft.Colors.with_opacity(0.05, self.c_yellow),
            border=ft.border.all(2, self.c_yellow),
            border_radius=20,
            padding=40,
            alignment=ft.alignment.center,
            margin=ft.margin.symmetric(horizontal=20),
            # Sombreado "Glow" Amarillo
            shadow=ft.BoxShadow(
                blur_radius=20,
                color=ft.Colors.with_opacity(0.2, self.c_yellow),
                spread_radius=0,
                offset=ft.Offset(0, 0)
            )
        )

    # --- RESTO DE MÉTODOS (Teclado, Sonidos, etc. sin cambios) ---
    def _build_keypad(self):
        ancho_btn = (self.ancho_fijo_contenido - 20) / 3 
        rows = []
        numeros = [['1', '2', '3'], ['4', '5', '6'], ['7', '8', '9']]
        for fila in numeros:
            row_controls = [self._create_key_btn(n, width=ancho_btn) for n in fila]
            rows.append(ft.Row(row_controls, spacing=10, alignment=ft.MainAxisAlignment.CENTER))
        
        rows.append(ft.Row([
            self._create_key_btn("Limpiar", is_action=True, color_base=self.c_red, width=ancho_btn),
            self._create_key_btn("0", width=ancho_btn),
            self._create_key_btn("⌫", is_action=True, color_base=self.c_yellow, width=ancho_btn)
        ], spacing=10, alignment=ft.MainAxisAlignment.CENTER))
        return ft.Column(rows, spacing=10)

    def _create_key_btn(self, text, width, is_action=False, color_base="#3b82f6"):
        return ft.Container(
            content=ft.Text(text, size=20 if not is_action else 14, weight="bold", color=color_base),
            width=width, height=75,
            alignment=ft.alignment.center,
            bgcolor=ft.Colors.with_opacity(0.05, color_base),
            border=ft.border.all(1, ft.Colors.with_opacity(0.2, color_base)),
            border_radius=10,
            ink=True,
            on_click=lambda _: self.controller.manejar_teclado(text)
        )

    def actualizar_dni_display(self, dni):
        self.txt_dni.value = dni.ljust(8, "_")
        self.txt_dni.update()
        if len(dni) == 8:
            self.btn_verificar.opacity = 1.0
            self.btn_verificar.disabled = False
        else:
            self.btn_verificar.opacity = 0.5
            self.btn_verificar.disabled = True
            
        self.btn_verificar.update()

    def mostrar_resultado(self, estado, data=None):
        self.contenedor_resultados.controls.clear()
        content = None
        if estado == "success": content = self._build_result_success(data)
        elif estado == "error": content = self._build_result_error(data)
        elif estado == "not_found": content = self._build_result_not_found(data)
        self.contenedor_resultados.controls.append(content)
        self.contenedor_resultados.update()

    def limpiar_resultado(self):
        # --- CORRECCIÓN AQUÍ: Verificamos si la página existe ---
        if self.contenedor_resultados.page:
            self.contenedor_resultados.controls.clear()
            self.contenedor_resultados.controls.append(self.estado_espera)
            self.contenedor_resultados.update()

    def reproducir_sonido(self, tipo):
        if tipo == "exito": self.audio_exito.play()
        elif tipo == "vencido": self.audio_vencido.play()
        elif tipo == "no_existe": self.audio_no_existe.play()
        elif tipo == "ya_asistio": self.audio_ya_asistio.play() 
        
        # Opcional: Proteger esto también si diera error, 
        # aunque self.page suele ser más robusto.
        if self.page:
            self.page.update()

    def _on_hover_admin(self, e):
        is_hover = e.data == "true"
        e.control.bgcolor = ft.Colors.with_opacity(0.1, self.c_blue_text) if is_hover else ft.Colors.TRANSPARENT
        e.control.update()