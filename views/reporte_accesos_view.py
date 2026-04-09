import flet as ft
from datetime import datetime
import math
from views.sidebar_view import Sidebar
from utils.audit_logger import AuditLogger

class ReporteAccesosView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/reporte_accesos")
        self.page = page
        self.bgcolor = "#0a0a0a"
        self.padding = 0
        
        self.logger = AuditLogger()
        self.datos_completos = [] 
        self.datos_filtrados = []
        self.filtro_fecha_seleccionada = None
        
        # --- CONFIGURACIÓN DE PAGINACIÓN ---
        self.pagina_actual = 1
        self.filas_por_pagina = 15
        self.total_paginas = 1

        user_actual = self.page.session.get("user") or "Usuario"
        self.sidebar = Sidebar(self.page, route_actual="/reporte_accesos", user=user_actual)

        # --- DATE PICKER ---
        self.date_picker = ft.DatePicker(
            on_change=self._on_date_change,
            cancel_text="Cancelar",
            confirm_text="Seleccionar",
            error_format_text="Fecha inválida",
            field_label_text="Ingrese una fecha",
            help_text="Seleccione día",
            first_date=datetime(2024, 1, 1),
            last_date=datetime(2030, 12, 31),
        )
        self.page.overlay.append(self.date_picker)

        # --- CONTROLES DE FILTRO ---
        self.txt_busqueda = ft.TextField(
            label="Buscar por usuario",
            prefix_icon=ft.icons.SEARCH,
            bgcolor="#18181b",
            border_color="#27272A",
            text_size=14,
            height=40,
            content_padding=10,
            on_change=self.aplicar_filtros,
            expand=True
        )

        self.btn_fecha = ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.CALENDAR_MONTH, color="#a1a1aa", size=18),
                ft.Text("Filtrar por fecha", ref=self._crear_ref_fecha(), color="#a1a1aa", size=14)
            ], alignment=ft.MainAxisAlignment.CENTER),
            bgcolor="#18181b",
            border=ft.border.all(1, "#27272A"),
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=15, vertical=8),
            on_click=lambda _: self.date_picker.pick_date(),
            ink=True
        )

        self.btn_limpiar = ft.IconButton(
            icon=ft.icons.FILTER_ALT_OFF,
            tooltip="Limpiar filtros",
            icon_color="#ef4444",
            on_click=self.limpiar_filtros
        )

        # --- TABLA ---
        self.tabla_accesos = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("DÍA", weight="bold", color="white")),
                ft.DataColumn(ft.Text("USUARIO", weight="bold", color="white")),
                ft.DataColumn(ft.Text("ENTRADA", weight="bold", color="white")),
                ft.DataColumn(ft.Text("SALIDA", weight="bold", color="white")),
            ],
            rows=[],
            border=ft.border.all(1, "#27272A"),
            heading_row_color="#18181b",
            data_row_color={"hovered": "#18181b"},
            divider_thickness=1,
            width=float("inf"),
            column_spacing=40,
        )

        # --- CONTROLES PAGINACIÓN ---
        self.btn_anterior = ft.IconButton(
            icon=ft.icons.KEYBOARD_ARROW_LEFT,
            icon_color="white",
            disabled=True,
            on_click=lambda _: self._cambiar_pagina(-1)
        )
        
        self.btn_siguiente = ft.IconButton(
            icon=ft.icons.KEYBOARD_ARROW_RIGHT,
            icon_color="white",
            disabled=True,
            on_click=lambda _: self._cambiar_pagina(1)
        )

        self.txt_info_pagina = ft.Text("Página 1 de 1", color="#a1a1aa", size=14)

        self.paginacion_container = ft.Row(
            controls=[
                self.btn_anterior,
                self.txt_info_pagina,
                self.btn_siguiente
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10
        )

        self.controls = [
            ft.Row([
                self.sidebar,
                ft.Container(
                    expand=True,
                    padding=40,
                    content=ft.Column([
                        ft.Text("Historial de Accesos", size=28, weight="bold", color="white"),
                        ft.Text("Registro detallado de actividad del personal", size=14, color="#a1a1aa"),
                        
                        ft.Container(height=10),

                        ft.Row([
                            ft.Container(self.txt_busqueda, width=300),
                            self.btn_fecha,
                            self.btn_limpiar
                        ], spacing=10),

                        ft.Container(height=10),
                        
                        # --- CONTENEDOR TABLA ---
                        ft.Container(
                            content=ft.Column(
                                [self.tabla_accesos], 
                                scroll=ft.ScrollMode.AUTO,
                            ),
                            expand=True,
                            border=ft.border.all(1, "#27272A"),
                            border_radius=10,
                            alignment=ft.alignment.top_center,
                            margin=ft.margin.symmetric(horizontal=100) # Mantiene el margen lateral
                        ),
                        
                        ft.Container(height=5),
                        self.paginacion_container
                    ])
                )
            ], expand=True, spacing=0)
        ]
        
        self.cargar_datos_iniciales()

    def _crear_ref_fecha(self):
        self.lbl_fecha_ref = ft.Ref[ft.Text]()
        return self.lbl_fecha_ref

    def _on_date_change(self, e):
        if self.date_picker.value:
            self.filtro_fecha_seleccionada = self.date_picker.value
            fecha_str = self.filtro_fecha_seleccionada.strftime("%d/%m/%Y")
            self.lbl_fecha_ref.current.value = fecha_str
            self.lbl_fecha_ref.current.color = "white"
            self.lbl_fecha_ref.current.update()
            self.aplicar_filtros()

    def limpiar_filtros(self, e):
        self.txt_busqueda.value = ""
        self.filtro_fecha_seleccionada = None
        self.lbl_fecha_ref.current.value = "Filtrar por fecha"
        self.lbl_fecha_ref.current.color = "#a1a1aa"
        self.txt_busqueda.update()
        self.lbl_fecha_ref.current.update()
        self.aplicar_filtros()

    def cargar_datos_iniciales(self):
        self.datos_completos = self.logger.obtener_historial()
        self.aplicar_filtros()

    def aplicar_filtros(self, e=None):
        filtro_nombre = self.txt_busqueda.value.lower() if self.txt_busqueda.value else ""
        
        self.datos_filtrados = []

        for item in self.datos_completos:
            usuario = item.get("usuario", "").lower()
            inicio_str = item.get("inicio", "")
            
            match_nombre = filtro_nombre in usuario
            match_fecha = True
            
            if self.filtro_fecha_seleccionada and inicio_str:
                try:
                    dt_inicio = datetime.strptime(inicio_str, "%Y-%m-%d %H:%M:%S")
                    if dt_inicio.date() != self.filtro_fecha_seleccionada.date():
                        match_fecha = False
                except:
                    match_fecha = False

            if match_nombre and match_fecha:
                self.datos_filtrados.append(item)

        self.pagina_actual = 1
        self._actualizar_vista_paginada()

    # --- LÓGICA DE PAGINACIÓN ---
    def _cambiar_pagina(self, delta):
        nueva_pagina = self.pagina_actual + delta
        if 1 <= nueva_pagina <= self.total_paginas:
            self.pagina_actual = nueva_pagina
            self._actualizar_vista_paginada()

    def _actualizar_vista_paginada(self):
        total_registros = len(self.datos_filtrados)
        self.total_paginas = math.ceil(total_registros / self.filas_por_pagina)
        
        if self.total_paginas == 0: self.total_paginas = 1 

        inicio = (self.pagina_actual - 1) * self.filas_por_pagina
        fin = inicio + self.filas_por_pagina
        
        datos_pagina = self.datos_filtrados[inicio:fin]
        
        self._renderizar_tabla(datos_pagina)
        
        self.txt_info_pagina.value = f"Página {self.pagina_actual} de {self.total_paginas}"
        self.btn_anterior.disabled = (self.pagina_actual == 1)
        self.btn_siguiente.disabled = (self.pagina_actual == self.total_paginas)
        
        if self.paginacion_container.page:
            self.paginacion_container.update()

    def _renderizar_tabla(self, datos):
        self.tabla_accesos.rows.clear()
        
        for item in datos:
            usuario = item.get("usuario", "Desc.")
            inicio_str = item.get("inicio", "")
            fin_str = item.get("fin")

            es_diego = (usuario == "Diego")
            color_usuario = "#ef4444" if es_diego else "white"
            icono = ft.icons.SECURITY if es_diego else ft.icons.PERSON

            texto_dia = "-"
            texto_entrada = "-"
            texto_salida = "--"
            
            if inicio_str:
                try:
                    dt_inicio = datetime.strptime(inicio_str, "%Y-%m-%d %H:%M:%S")
                    texto_dia = self.obtener_dia_esp(dt_inicio)
                    texto_entrada = self.obtener_hora(dt_inicio)
                except: pass

            if fin_str:
                try:
                    dt_fin = datetime.strptime(fin_str, "%Y-%m-%d %H:%M:%S")
                    texto_salida = self.obtener_hora(dt_fin)
                except: pass
            else:
                texto_salida = "EN CURSO"

            # --- LÓGICA DE COLORES CORREGIDA ---
            # Entrada: VERDE
            color_entrada = "#22c55e"
            
            # Salida: ROJO (o Azul si está en curso para diferenciar)
            color_salida = "#ef4444" 
            if texto_salida == "EN CURSO":
                color_salida = "#3b82f6" # Azul para indicar 'Activo'

            self.tabla_accesos.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(texto_dia, color="#a1a1aa", size=13)),
                    ft.DataCell(ft.Row([
                        ft.Icon(icono, color=color_usuario, size=16),
                        ft.Text(usuario.upper(), color="white", weight="bold" if es_diego else "normal")
                    ])),
                    # Columna ENTRADA (Verde)
                    ft.DataCell(ft.Text(texto_entrada, color=color_entrada, weight="bold")),
                    # Columna SALIDA (Rojo)
                    ft.DataCell(ft.Text(texto_salida, color=color_salida, weight="bold" if texto_salida == "EN CURSO" else "normal")),
                ])
            )
        
        if self.tabla_accesos.page:
            self.tabla_accesos.update()

    def obtener_dia_esp(self, dt):
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        nombre_dia = dias[dt.weekday()]
        fecha_corta = dt.strftime("%d/%m")
        return f"{nombre_dia} {fecha_corta}"

    def obtener_hora(self, dt):
        return dt.strftime("%H:%M")