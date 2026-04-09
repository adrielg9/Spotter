import flet as ft
from utils.theme import AppTheme

class EditarSocioView(ft.View):
    def __init__(self, page):
        super().__init__(route="/editar_socio")
        self.page = page
        self.controller = None 

        self.bgcolor = AppTheme.bgcolor
        self.padding = 0 
        self.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        # --- CONTENEDOR DE MENSAJES ---
        self.status_text = ft.Text("", size=14, weight="bold", color="white")
        self.status_icon = ft.Icon(ft.icons.INFO, color="white", size=20)
       
        self.status_container = ft.Container(
            content=ft.Row(
                controls=[
                    self.status_icon,
                    ft.Container(content=self.status_text, expand=True) 
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10
            ),
            padding=12,
            border_radius=10,
            visible=False, 
            alignment=ft.alignment.center
        )

        # --- ESTILOS DE INPUTS ---
        def get_input_props(label, icon, is_read_only=False):
            return {
                "label": label,
                "prefix_icon": icon,
                "border_radius": 12,
                "border_color": ft.Colors.with_opacity(0.3, AppTheme.text_secondary),
                "focused_border_color": AppTheme.primary,
                "text_size": 15,
                "color": AppTheme.text_primary,
                "label_style": ft.TextStyle(color=AppTheme.text_secondary),
                "bgcolor": ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
                "height": 60,
                "content_padding": 18,
                "read_only": is_read_only 
            }

        # --- ELEMENTOS VISUALES ---
        self.avatar = ft.Container(
            content=ft.Icon(ft.icons.PERSON_ROUNDED, size=60, color=AppTheme.bgcolor),
            width=100, height=100,
            bgcolor=AppTheme.primary,
            border_radius=50,
            alignment=ft.alignment.center,
            shadow=ft.BoxShadow(blur_radius=20, color=ft.Colors.with_opacity(0.4, AppTheme.primary))
        )

        self.titulo_lbl = ft.Text("Editar Socio", size=24, weight="bold", color=AppTheme.text_primary)
        self.subtitulo_lbl = ft.Text("Actualiza la información de contacto", size=13, color=AppTheme.text_secondary)

        self.txt_dni = ft.TextField(**get_input_props("DNI / Identificación", ft.icons.LOCK_OUTLINE, is_read_only=True))
        self.txt_dni.suffix = ft.Icon(ft.icons.BLOCK, size=20, color=ft.Colors.GREY_600)
        
        self.txt_nombre = ft.TextField(**get_input_props("Nombre Completo", ft.icons.PERSON_OUTLINE_ROUNDED))
        self.txt_tel = ft.TextField(**get_input_props("Teléfono / Móvil", ft.icons.PHONE_IPHONE_ROUNDED), max_length=15, input_filter=ft.NumbersOnlyInputFilter())
        
        # --- 4. BOTONES EN LA MISMA FILA ---

        # Botón Volver (Izquierda)
        self.btn_cancelar = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.icons.ARROW_BACK, color="#a1a1aa", size=18), 
                    # Abreviamos un poco el texto para que entre bien
                    ft.Text("VOLVER", color="#a1a1aa", weight="bold", size=13)
                ], 
                alignment=ft.MainAxisAlignment.CENTER, spacing=5
            ),
            bgcolor="#27272A", 
            border=ft.border.all(1, "#3f3f46"),
            border_radius=12,
            padding=15,
            on_click=self.cancelar,
            expand=True, # <--- IMPORTANTE: Ocupa el 50% del ancho
            ink=True
        )

        # Botón Guardar (Derecha)
        self.btn_actualizar = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.icons.CHECK_CIRCLE_ROUNDED, color=ft.Colors.WHITE, size=18), 
                    ft.Text("GUARDAR", color=ft.Colors.WHITE, weight="bold", size=13)
                ], 
                alignment=ft.MainAxisAlignment.CENTER, spacing=5
            ),
            bgcolor=AppTheme.primary,
            border_radius=12,
            padding=15,
            on_click=self.guardar_cambios,
            shadow=ft.BoxShadow(blur_radius=15, color=ft.Colors.with_opacity(0.4, AppTheme.primary)),
            expand=True, # <--- IMPORTANTE: Ocupa el 50% del ancho
            ink=True
        )

        # --- LAYOUT FINAL ---
        card_content = ft.Column(
            [
                ft.Container(
                    content=ft.Column([
                        self.avatar,
                        ft.Container(height=10),
                        self.titulo_lbl,
                        self.subtitulo_lbl
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                    alignment=ft.alignment.center,
                    padding=ft.padding.only(bottom=20)
                ),

                ft.Divider(color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE), thickness=1),
                ft.Container(height=10),

                self.txt_dni,
                ft.Container(height=5),
                self.txt_nombre,
                ft.Container(height=5),
                self.txt_tel,
                
                ft.Container(height=15),
                self.status_container,
                ft.Container(height=15),

                # --- FILA DE BOTONES ---
                ft.Row(
                    controls=[
                        self.btn_cancelar, 
                        self.btn_actualizar
                    ],
                    spacing=15, # Espacio entre los dos botones
                    alignment=ft.MainAxisAlignment.CENTER
                )
                # -----------------------
            ],
            spacing=5
        )

        # Contenedor de la Tarjeta
        self.form_card = ft.Container(
            content=card_content,
            width=420, 
            padding=35, 
            bgcolor=AppTheme.card_color, 
            border_radius=25,
            shadow=ft.BoxShadow(
                blur_radius=60, 
                color=ft.Colors.with_opacity(0.15, "#000000"), 
                offset=ft.Offset(0, 10)
            ),
            border=ft.border.all(1, ft.Colors.with_opacity(0.08, ft.Colors.WHITE))
        )

        self.controls = [self.form_card]

    # --- LÓGICA ---
    def set_controller(self, controller):
        self.controller = controller
        self.controller.cargar_datos_edicion() 

    def guardar_cambios(self, e):
        if self.controller: self.controller.actualizar_socio(e)

    def cancelar(self, e):
        self.page.go("/lista")
        
    def mostrar_mensaje(self, msg, color="green"):
        if color == "red":
            bg_color = ft.Colors.with_opacity(0.1, ft.Colors.RED)
            border_color = ft.Colors.RED_400
            icono = ft.icons.ERROR_OUTLINE
            text_color = ft.Colors.RED_200
        elif color == "orange":
            bg_color = ft.Colors.with_opacity(0.1, ft.Colors.ORANGE)
            border_color = ft.Colors.ORANGE_400
            icono = ft.icons.WARNING_AMBER_ROUNDED
            text_color = ft.Colors.ORANGE_200
        else:
            bg_color = ft.Colors.with_opacity(0.1, ft.Colors.GREEN)
            border_color = ft.Colors.GREEN_400
            icono = ft.icons.CHECK_CIRCLE_OUTLINE
            text_color = ft.Colors.GREEN_200

        self.status_text.value = msg
        self.status_text.color = text_color
        self.status_text.text_align = ft.TextAlign.LEFT

        self.status_icon.name = icono
        self.status_icon.color = text_color
        
        self.status_container.bgcolor = bg_color
        self.status_container.border = ft.border.all(1, border_color)
        
        self.status_container.visible = True
        self.update()
    
    def rellenar_datos(self, socio):
        self.txt_dni.value = str(socio['dni'])
        self.txt_nombre.value = socio['nombre']
        self.txt_tel.value = socio['telefono']
        self.update()