import flet as ft
from utils.theme import AppTheme
from views.sidebar_view import Sidebar

class RegistroSocioView(ft.View):
    def __init__(self, page):
        super().__init__(route="/registro")
        self.page = page
        self.controller = None 
        self.bgcolor = "#09090b" 
        self.padding = 0 
        
        self.user_sesion = self.page.session.get("user") or "Usuario"
        
        # Estado interno
        self.selected_membership = "Musculación"
        self.selected_method = "Efectivo"

        # --- PALETA ---
        self.c_border = "#27272a"      
        self.c_focus = "#3b82f6"       
        self.c_input_bg = "#000000"    
        self.c_card_bg = "#18181b"     
        self.c_text_muted = "#a1a1aa"
        self.c_error = "#ef4444" 

        # --- 1. DEFINIR INPUTS (Equilibrados: Texto 14, Alto 44) ---
        def create_textfield(hint, is_number=False, only_numbers=False, max_digits=None):
            if only_numbers and max_digits:
                filtro = ft.InputFilter(allow=True, regex_string=rf"^[0-9]{{0,{max_digits}}}$", replacement_string="")
            elif only_numbers:
                filtro = ft.InputFilter(allow=True, regex_string=r"^[0-9]*$", replacement_string="")
            else:
                filtro = None
            return ft.TextField(
                hint_text=hint,
                hint_style=ft.TextStyle(color="#52525b", size=14),
                text_size=14, # Tamaño ideal de lectura
                color="white",
                bgcolor=self.c_input_bg,
                border_color=self.c_border,
                focused_border_color=self.c_focus,
                border_radius=8,
                content_padding=12,
                keyboard_type=ft.KeyboardType.NUMBER if is_number else ft.KeyboardType.TEXT,
                input_filter=filtro,
                max_length=max_digits if max_digits else None,
                height=44, # Altura intermedia para ahorrar espacio vertical
                cursor_color=self.c_focus,
                animate_size=200,
            )

        self.txt_nombre = create_textfield("Juan")
        self.txt_apellido = create_textfield("Pérez")
        self.txt_dni = create_textfield("12345678", is_number=True, only_numbers=True, max_digits=8)
        self.txt_tel = create_textfield("1112345678", is_number=True, only_numbers=True)
        
        # Campo Monto
        self.txt_monto = create_textfield("15000", is_number=True, only_numbers=True)
        self.txt_monto.width = 200
        self.txt_monto.text_align = ft.TextAlign.LEFT 
        self.txt_monto.prefix_text = "$ " 
        self.txt_monto.prefix_style = ft.TextStyle(color=self.c_text_muted, size=14)

        # --- 2. TEXTOS DE ERROR ---
        def create_error_text():
            return ft.Text("", color=self.c_error, size=11, weight="w500", visible=False)

        self.err_nombre = create_error_text()
        self.err_apellido = create_error_text()
        self.err_dni = create_error_text()
        self.err_tel = create_error_text()
        self.err_monto = create_error_text()

        # --- 3. WRAPPER ---
        def field_wrapper(label, control, error_control, expand=True):
            return ft.Column([
                ft.Text(label, color="white", size=14, weight="w500"),
                control,
                error_control 
            ], spacing=2, expand=expand)

        # --- 4. CONSTRUCCIÓN VISUAL ---
        header = ft.Column([
            ft.Text("Nuevo Alumno", size=26, weight="bold", color="white"),
            ft.Text("Complete los datos del formulario", size=14, color=self.c_text_muted)
        ], spacing=2)

        # FILA 1
        row_names = ft.Row([
            field_wrapper("Nombre *", self.txt_nombre, self.err_nombre),
            field_wrapper("Apellido *", self.txt_apellido, self.err_apellido)
        ], spacing=15) 

        # FILA 2
        row_contact = ft.Row([
            field_wrapper("DNI *", self.txt_dni, self.err_dni),
            field_wrapper("Teléfono *", self.txt_tel, self.err_tel)
        ], spacing=15)

        # FILA 3: MEMBRESÍA
        self.opt_musculacion = self._build_option_card("Musculación", selected=True)
        self.opt_bodypump = self._build_option_card("Body Pump", selected=False)
        self.opt_combo = self._build_option_card("Musc. + Pump", selected=False)

        section_membership = ft.Column([
            ft.Text("Membresía *", size=14, color="white", weight="w500"),
            ft.Row([self.opt_musculacion, self.opt_bodypump, self.opt_combo], spacing=10, expand=True)
        ], spacing=5) 

        # FILA 4: PAGO
        self.opt_efectivo = self._build_method_card("Efectivo", selected=True)
        self.opt_transferencia = self._build_method_card("Transferencia", selected=False)

        section_method = ft.Column([
            ft.Text("Método de Pago *", size=14, color="white", weight="w500"),
            ft.Row([self.opt_efectivo, self.opt_transferencia], spacing=10)
        ], spacing=5)

        # FILA 5: MONTO
        section_amount = ft.Column([
             ft.Text("Cuota Mensual *", color="white", size=14, weight="w500"),
             self.txt_monto,
             self.err_monto
        ], spacing=2)

        # BOTÓN GUARDAR
        self.btn_guardar = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.SAVE, color="white", size=20),
                ft.Text("Guardar Alumno", color="white", weight="bold", size=15)
            ], alignment=ft.MainAxisAlignment.CENTER),
            bgcolor=self.c_focus,
            padding=14,
            border_radius=10,
            ink=True,
            width=260, 
            on_click=self.guardar,
            on_hover=lambda e: self._animate_button(e.control, e.data)
        )

        form_card = ft.Container(
            content=ft.Column([
                header,
                ft.Divider(height=8, color="transparent"),
                row_names,
                row_contact,
                ft.Divider(height=8, color="#27272a", thickness=0.5),
                section_membership,
                ft.Divider(height=5, color="transparent"),
                section_method,
                ft.Divider(height=5, color="transparent"),
                section_amount,
                ft.Divider(height=15, color="transparent"),
                ft.Row([self.btn_guardar], alignment=ft.MainAxisAlignment.CENTER),
            ], spacing=10), # Espaciado vertical controlado
            
            bgcolor=self.c_card_bg,
            border=ft.border.all(1, self.c_border),
            border_radius=16,
            padding=30,
            width=880 
        )

        self.controls = [
            ft.Row([
                Sidebar(self.page, "/registro", user=self.user_sesion),
                ft.Container(
                    content=form_card,
                    expand=True,
                    alignment=ft.alignment.center,
                    padding=10
                )
            ], expand=True, spacing=0)
        ]

    # --- UI HELPERS ---
    def _build_option_card(self, text, selected):
        border_c = self.c_focus if selected else self.c_border
        bg_c = ft.Colors.with_opacity(0.1, self.c_focus) if selected else "transparent"
        icon_c = self.c_focus if selected else "#52525b"
        return ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.RADIO_BUTTON_CHECKED if selected else ft.Icons.RADIO_BUTTON_UNCHECKED, color=icon_c, size=18),
                ft.Text(text, color="white", weight="w500", size=13) 
            ], spacing=10, alignment=ft.MainAxisAlignment.CENTER),
            padding=10,
            border=ft.border.all(1, border_c),
            border_radius=8,
            bgcolor=bg_c,
            expand=True,
            animate=ft.animation.Animation(150, "easeOut"),
            on_click=lambda e: self._select_membership(text),
            data=text
        )
    
    def _build_method_card(self, text, selected):
        border_c = self.c_focus if selected else self.c_border
        bg_c = ft.Colors.with_opacity(0.1, self.c_focus) if selected else "transparent"
        return ft.Container(
            content=ft.Text(text, color="white", weight="w500", size=13, text_align="center"),
            padding=10,
            border=ft.border.all(1, border_c),
            border_radius=8,
            bgcolor=bg_c,
            expand=True,
            animate=ft.animation.Animation(150, "easeOut"),
            on_click=lambda e: self._select_method(text),
            data=text
        )

    def _select_membership(self, valor):
        val_real = "Body Pump + Musculación" if valor == "Musc. + Pump" else valor
        self.selected_membership = val_real
        self._update_cards([self.opt_musculacion, self.opt_bodypump, self.opt_combo], valor)

    def _select_method(self, valor):
        self.selected_method = valor
        self._update_cards([self.opt_efectivo, self.opt_transferencia], valor, is_method=True)

    def _update_cards(self, cards, valor_seleccionado, is_method=False):
        for card in cards:
            es_este = card.data == valor_seleccionado
            card.border = ft.border.all(1, self.c_focus if es_este else self.c_border)
            card.bgcolor = ft.Colors.with_opacity(0.1, self.c_focus) if es_este else "transparent"
            if not is_method:
                icon = card.content.controls[0]
                icon.name = ft.Icons.RADIO_BUTTON_CHECKED if es_este else ft.Icons.RADIO_BUTTON_UNCHECKED
                icon.color = self.c_focus if es_este else "#52525b"
            card.update()

    def _animate_button(self, btn, is_hover):
        btn.opacity = 0.9 if is_hover == "true" else 1.0
        btn.update()

    # --- MANEJO DE ERRORES ---
    def limpiar_errores(self):
        for campo in [self.txt_nombre, self.txt_apellido, self.txt_dni, self.txt_tel, self.txt_monto]:
            campo.border_color = self.c_border
        for err in [self.err_nombre, self.err_apellido, self.err_dni, self.err_tel, self.err_monto]:
            err.value = ""
            err.visible = False
        self.update()

    def mostrar_error(self, nombre_campo, mensaje):
        campo = None
        err_lbl = None
        if nombre_campo == "nombre": campo, err_lbl = self.txt_nombre, self.err_nombre
        elif nombre_campo == "apellido": campo, err_lbl = self.txt_apellido, self.err_apellido
        elif nombre_campo == "dni": campo, err_lbl = self.txt_dni, self.err_dni
        elif nombre_campo == "telefono": campo, err_lbl = self.txt_tel, self.err_tel
        elif nombre_campo == "monto": campo, err_lbl = self.txt_monto, self.err_monto
        
        if campo and err_lbl:
            campo.border_color = self.c_error
            err_lbl.value = mensaje
            err_lbl.visible = True
            self.update()

    def set_controller(self, controller):
        self.controller = controller

    def obtener_datos(self):
        act = self.selected_membership
        if act == "Musc. + Pump": act = "Body Pump + Musculación"
        return {
            "dni": self.txt_dni.value, 
            "nombre": self.txt_nombre.value,
            "apellido": self.txt_apellido.value,
            "telefono": self.txt_tel.value,
            "actividad": act,
            "metodo": self.selected_method,
            "monto": self.txt_monto.value
        }

    def guardar(self, e):
        if self.controller: self.controller.guardar_socio(e)

    def cancelar(self, e):
        if self.controller: self.controller.cancelar_formulario()

    def mostrar_mensaje(self, msg, color="green"):
        bg = AppTheme.error if color in ["orange", "red"] else AppTheme.success
        self.page.open(ft.SnackBar(ft.Text(msg, color=ft.Colors.WHITE), bgcolor=bg))

    # --- DIÁLOGO DE ÉXITO PROFESIONAL ---
    def mostrar_exito(self, nombre):
        def cerrar(e):
            self.page.close(dialog)
            self.controller.ir_al_inicio()

        content = ft.Column(
            [
                ft.Container(
                    content=ft.Icon(ft.icons.CHECK_ROUNDED, size=50, color="#22c55e"),
                    bgcolor=ft.colors.with_opacity(0.1, "#22c55e"),
                    padding=20,
                    shape=ft.BoxShape.CIRCLE,
                    border=ft.border.all(2, ft.colors.with_opacity(0.2, "#22c55e")),
                ),
                
                ft.Container(height=10), 

                ft.Text("¡Registro Exitoso!", size=22, weight="bold", color="white"),
                ft.Text(
                    f"El socio {nombre}\nha sido guardado correctamente.", 
                    size=14, 
                    color="#a1a1aa", 
                    text_align="center"
                ),

                ft.Container(height=20), 

                ft.Container(
                    content=ft.Text("Aceptar", weight="bold", color="white"),
                    bgcolor="#22c55e",
                    padding=ft.padding.symmetric(vertical=12),
                    width=200,
                    border_radius=10,
                    alignment=ft.alignment.center,
                    on_click=cerrar,
                    ink=True, 
                    shadow=ft.BoxShadow(
                        blur_radius=15, 
                        color=ft.colors.with_opacity(0.4, "#22c55e")
                    )
                )
            ],
            tight=True, 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5
        )

        dialog = ft.AlertDialog(
            content=ft.Container(
                content=content,
                padding=20,
                width=300 
            ),
            bgcolor="#18181b", 
            shape=ft.RoundedRectangleBorder(radius=20), 
            modal=True, 
        )

        self.page.open(dialog)

    def mostrar_loading(self):
        self.btn_guardar.content = ft.Row([ft.ProgressRing(width=16, height=16, color="white"), ft.Text("Procesando...", color="white")], alignment=ft.MainAxisAlignment.CENTER)
        self.btn_guardar.disabled = True
        self.btn_guardar.update()

    def ocultar_loading(self):
        self.btn_guardar.content = ft.Row([ft.Icon(ft.Icons.SAVE, color="white", size=20), ft.Text("Guardar Alumno", color="white", weight="bold", size=15)], alignment=ft.MainAxisAlignment.CENTER)
        self.btn_guardar.disabled = False
        self.btn_guardar.update()
        
    def rellenar_formulario(self, socio):
        self.txt_dni.value = str(socio['dni'])
        nombre_completo = socio['nombre'].strip()
        if " " in nombre_completo:
            parts = nombre_completo.split(" ", 1)
            self.txt_nombre.value = parts[0]
            self.txt_apellido.value = parts[1]
        else:
            self.txt_nombre.value = nombre_completo
        self.txt_tel.value = socio['telefono']
        self.update()
        
    def limpiar_formulario(self):
        self.limpiar_errores()
        self.txt_dni.value = ""
        self.txt_nombre.value = ""
        self.txt_apellido.value = ""
        self.txt_tel.value = ""
        self.txt_monto.value = ""
        self._select_membership("Musculación")
        self._select_method("Efectivo")
        self.update()