import flet as ft

from views.sidebar_view import Sidebar 

class PagoView(ft.View):
    def __init__(self, page):
        super().__init__(route="/pagos")
        self.page = page
        self.controller = None 
        self.bgcolor = "#09090b" 
        self.padding = 0 

        # --- 0. RECUPERAR USUARIO DE SESIÓN ---
        self.user_sesion = self.page.session.get("user") or "Usuario"
        self.c_gris_borde = "#71717a" 

        # --- 1. COMPONENTES DE BÚSQUEDA ---
        self.txt_busqueda = ft.TextField(
            hint_text="Buscar...", # Ayuda visual interna
            prefix_icon=ft.icons.SEARCH_ROUNDED,
            border_radius=12,
            bgcolor=ft.Colors.TRANSPARENT, 
            border_color=self.c_gris_borde, 
            focused_border_color="#3b82f6",
            height=50,
            text_size=15,
            on_change=lambda e: self.controller.filtrar_sugerencias(e)
        )

        self.lista_resul = ft.ListView(expand=True, spacing=5, height=200)
        self.card_sugerencias = ft.Container(
            content=self.lista_resul,
            visible=False,
            bgcolor=ft.Colors.TRANSPARENT, 
            border=ft.border.all(1, self.c_gris_borde), 
            border_radius=12,
            padding=10
        )

        # --- 2. ESTADO INICIAL (ÍCONO Y TEXTO) ---
        self.contenedor_estado_inicial = ft.Column([
            ft.Divider(height=40, color="transparent"),
            ft.Icon(ft.icons.CREDIT_CARD_ROUNDED, size=80, color="#27272a"),
            ft.Text(
                "Busque un alumno para registrar su pago", 
                color="#52525b", 
                size=16, 
                text_align="center"
            ),
            ft.Divider(height=20, color="transparent"),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, visible=True)

        # --- 3. COMPONENTES DEL FORMULARIO DE PAGO ---
        self.lbl_socio_sel = ft.Text("", size=18, weight="bold", color="#3b82f6")
        
        # 1. DESPLEGABLE DE ACTIVIDAD
        self.dd_actividad = ft.Dropdown(
            label="Tipo de Cuota", 
            border_radius=10, 
            
            # TRUCO: Usamos el mismo color del fondo (o un gris muy oscuro)
            # En vez de TRANSPARENT, usamos este gris carbón que "camufla" el input
            bgcolor="#18181b",  
            
            # Opcional: Si quieres que cambie un poco al hacer clic
            focused_bgcolor="#1f1f22",
            
            border_color=self.c_gris_borde,
            focused_border_color="#3b82f6",
            options=[
                ft.dropdown.Option("Body Pump"),
                ft.dropdown.Option("Musculación"),
                ft.dropdown.Option("Body Pump + Musculación"),
            ], 
            expand=True
        )

        # 2. DESPLEGABLE DE MÉTODO DE PAGO
        self.dd_metodo = ft.Dropdown(
            label="Método de Pago", 
            border_radius=10,
            
            # TRUCO: Mismo color sólido oscuro
            bgcolor="#18181b", 
            
            focused_bgcolor="#1f1f22",
            
            border_color=self.c_gris_borde,
            focused_border_color="#3b82f6",
            options=[
                ft.dropdown.Option("Efectivo"), 
                ft.dropdown.Option("Transferencia")
            ],
            expand=True 
        )
        
        self.txt_monto = ft.TextField(
            label="Monto ($)", border_radius=10,
            bgcolor=ft.Colors.TRANSPARENT, border_color=self.c_gris_borde,
            keyboard_type=ft.KeyboardType.NUMBER, expand=True
        )
        
        self.btn_confirmar = ft.ElevatedButton(
            "Confirmar Pago", bgcolor="#22c55e", color="white", height=45,
            on_click=lambda e: self.controller.registrar_pago(e)
        )

        # Agrupamos el formulario para controlar su visibilidad
        self.columna_formulario = ft.Column([
            self.lbl_socio_sel,
            ft.Container(height=10),
            ft.Row([self.dd_actividad, self.txt_monto], spacing=15),
            ft.Container(height=10),
            ft.Row([self.dd_metodo]), 
            ft.Container(height=20),
            ft.Row([
                ft.ElevatedButton(
                    "Cancelar", bgcolor="#4b5563", color="white", height=45,
                    on_click=lambda e: self.controller.cancelar(e)
                ),
                self.btn_confirmar
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        ], visible=False)

        # --- 4. CABECERA ---
        cabecera = ft.Row([
            ft.Column([
                ft.Text("Registro de Pagos", size=24, weight="bold", color="white"),
                ft.Text("Actualice las cuotas de los alumnos", size=14, color="#a1a1aa"),
            ], spacing=0)
        ], alignment=ft.MainAxisAlignment.START)

        # --- 5. ESTRUCTURA DE LA TARJETA ---
        self.tarjeta_cobro = ft.Container(
            content=ft.Column([
                # Texto arriba del buscador
                ft.Text("Buscar Alumno por Nombre o DNI", color="white", size=14, weight="w500"),
                self.txt_busqueda,
                self.card_sugerencias,
                
                # Aquí alternamos entre el estado inicial y el formulario
                self.contenedor_estado_inicial,
                self.columna_formulario,
                
            ], tight=True),
            padding=40, 
            bgcolor=ft.Colors.TRANSPARENT,
            border=ft.border.all(1, "#27272a"), 
            border_radius=20, 
            width=550, 
            shadow=ft.BoxShadow(blur_radius=50, color=ft.Colors.with_opacity(0.4, "black"))
        )

        # --- 6. ARMADO FINAL ---
        area_derecha = ft.Container(
            content=ft.Column([
                cabecera,
                ft.Container(expand=True, content=self.tarjeta_cobro, alignment=ft.alignment.center),
            ], expand=True, spacing=0),
            expand=True,
            padding=ft.padding.only(top=30, left=40, right=40, bottom=40) 
        )

        self.controls = [
            ft.Row([
                Sidebar(self.page, "/pagos", user=self.user_sesion),
                area_derecha
            ], expand=True, spacing=0)
        ]

    # --- MÉTODOS DE INTERFAZ ---

    def mostrar_sugerencias(self, socios):
        self.lista_resul.controls.clear()
        for s in socios:
            self.lista_resul.controls.append(
                ft.ListTile(
                    leading=ft.Icon(ft.icons.PERSON_SEARCH_ROUNDED, color="#3b82f6"),
                    title=ft.Text(s['nombre'], weight="bold", size=14),
                    subtitle=ft.Text(f"DNI: {s['dni']}", size=12),
                    on_click=lambda _, socio=s: self.controller.seleccionar_socio(socio)
                )
            )
        self.card_sugerencias.visible = len(socios) > 0
        self.update()

    def preparar_formulario_pago(self, socio):
        """Muestra el formulario y oculta el estado inicial"""
        self.card_sugerencias.visible = False
        self.contenedor_estado_inicial.visible = False # Ocultar ícono/ayuda
        self.columna_formulario.visible = True        # Mostrar campos
        
        self.lbl_socio_sel.value = f"Socio: {socio['nombre']}"
        self.txt_busqueda.value = socio['dni']
        self.dd_metodo.value = "Efectivo"
        self.dd_actividad.value = socio.get('actividad', "Musculación") 
        self.update()

    def limpiar_todo(self):
        """Vuelve al estado inicial con el ícono de tarjeta"""
        self.txt_busqueda.value = ""
        self.lbl_socio_sel.value = ""
        self.contenedor_estado_inicial.visible = True # Volver a mostrar ayuda
        self.columna_formulario.visible = False      # Ocultar campos
        self.card_sugerencias.visible = False
        self.update()

    def mostrar_mensaje(self, msg, color="green"):
        self.page.open(ft.SnackBar(ft.Text(msg), bgcolor=color))

    def set_controller(self, ctrl):
        self.controller = ctrl