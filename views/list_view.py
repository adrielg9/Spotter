import flet as ft
from utils.theme import AppTheme
from views.sidebar_view import Sidebar

class ListaSociosView(ft.View):
    def __init__(self, page):
        super().__init__(route="/lista")
        self.page = page
        self.controller = None 
        self.bgcolor = "#09090b" 
        self.padding = 0

        # --- CONTADORES ---
        self.txt_total_socios = ft.Text("0", size=26, weight="bold", color="white")
        self.txt_al_dia = ft.Text("0", size=26, weight="bold", color="#22c55e")
        self.txt_con_deuda = ft.Text("0", size=26, weight="bold", color="#ef4444")

        # --- TABLA DE DATOS ---
        self.tabla = ft.DataTable(
            width=float("inf"),
            heading_row_color=ft.Colors.with_opacity(0.05, "white"),
            heading_row_height=55, 
            data_row_max_height=60, 
            column_spacing=20, 
            divider_thickness=1,
            horizontal_lines=ft.border.BorderSide(0.5, "#27272a"),
            columns=[
                ft.DataColumn(ft.Text("ALUMNO", size=12, weight="bold", color="#a1a1aa")),
                ft.DataColumn(ft.Text("DNI", size=12, weight="bold", color="#a1a1aa")),
                ft.DataColumn(ft.Text("TELÉFONO", size=12, weight="bold", color="#a1a1aa")),
                ft.DataColumn(ft.Text("ACTIVIDAD", size=12, weight="bold", color="#a1a1aa")),
                ft.DataColumn(ft.Text("VENCIMIENTO", size=12, weight="bold", color="#a1a1aa")),
                ft.DataColumn(ft.Text("ESTADO", size=12, weight="bold", color="#a1a1aa")),
                ft.DataColumn(ft.Text("ACCIONES", size=12, weight="bold", color="#a1a1aa")),
            ],
            rows=[]
        )

        # --- NAVEGACIÓN ---
        self.btn_ant = ft.IconButton(ft.icons.CHEVRON_LEFT_ROUNDED, icon_color="white", on_click=lambda _: self.controller.cambiar_pagina(-1))
        self.btn_sig = ft.IconButton(ft.icons.CHEVRON_RIGHT_ROUNDED, icon_color="white", on_click=lambda _: self.controller.cambiar_pagina(1))
        self.txt_paginacion = ft.Text("1 / 1", color="white54", size=13)

        # --- CABECERA ---
        cabecera = ft.Column([
            ft.Row([
                ft.IconButton(ft.icons.ARROW_BACK_IOS_NEW_ROUNDED, icon_size=16, icon_color="white", on_click=lambda _: self.page.go("/home")),
                ft.Column([
                    ft.Text("Listado de Alumnos", size=26, weight="bold", color="white"),
                    ft.Text("Gestione todos los miembros del gimnasio", size=14, color="#a1a1aa"),
                ], spacing=0)
            ], spacing=10),
            
            ft.Row([
                self._build_stat_card("Total", self.txt_total_socios, ft.icons.PEOPLE_ALT_ROUNDED, "#3b82f6"),
                self._build_stat_card("Al Día", self.txt_al_dia, ft.icons.CHECK_CIRCLE_ROUNDED, "#22c55e"),
                self._build_stat_card("Deuda", self.txt_con_deuda, ft.icons.ERROR_ROUNDED, "#ef4444"),
            ], spacing=15),
            
            ft.Container(
                content=ft.Row([
                    ft.TextField(
                        hint_text="Buscar socio por Nombre o DNI...",
                        prefix_icon=ft.icons.SEARCH,
                        bgcolor="#18181b",
                        border_color="#27272a",
                        border_radius=10,
                        height=42, 
                        text_size=14,
                        expand=True,
                        on_change=lambda e: self.controller.filtrar_socios(e.control.value)
                    ),
                    ft.Row([
                        self._build_filter_btn("Todos", "TODOS"),
                        self._build_filter_btn("Al Día", "AL_DIA"),
                        self._build_filter_btn("Vencidos", "VENCIDO"),
                        self._build_filter_btn("Inactivos", "INACTIVO"),
                    ], spacing=5)
                ], spacing=15),
            )
        ], spacing=10)

        # --- ÁREA DE TABLA (CON SCROLL CORREGIDO) ---
        # Definimos la columna scrolleable por separado
        columna_tabla = ft.Column(
            controls=[self.tabla],
            scroll=ft.ScrollMode.AUTO, # Habilita el scroll si el contenido excede el alto
            spacing=0,
            expand=True # Importante para que ocupe todo el alto del contenedor padre
        )

        # --- ÁREA DE TABLA ---
        area_tabla = ft.Container(
            content=columna_tabla,
            expand=True, # ESTO ES CLAVE: Ocupar todo el espacio vertical disponible
            bgcolor="transparent",
            border=ft.border.all(1, "#27272a"),
            border_radius=15,
            padding=ft.padding.only(top=10, bottom=10), # Padding interno
            margin=ft.margin.symmetric(horizontal=30),  # Margen externo (antes estaba en el contenedor padre)
            alignment=ft.alignment.top_center
        )

        # --- ESTRUCTURA PRINCIPAL ---
        area_principal = ft.Container(
            content=ft.Column([
                # 1. Cabecera (Fija)
                ft.Container(cabecera, padding=ft.padding.symmetric(horizontal=30, vertical=20)),
                
                ft.Divider(height=1, color="#27272a"),
                
                # 2. Tabla (Expansible y Scrolleable)
                # Al ponerlo directo en la Columna con expand=1, obliga al scroll a activarse
                # si la tabla es más grande que este espacio.
                area_tabla, 
                
                ft.Divider(height=1, color="#27272a"),
                
                # 3. Footer / Paginación (Fijo abajo)
                ft.Container(
                    content=ft.Row([self.btn_ant, self.txt_paginacion, self.btn_sig], alignment=ft.MainAxisAlignment.CENTER),
                    padding=ft.padding.symmetric(horizontal=30, vertical=10)
                )
            ], spacing=0),
            expand=True,
            bgcolor="#09090b"
        )

        user_sesion = self.page.session.get("user") or "Usuario"

        self.controls = [
            ft.Row([
                Sidebar(self.page, "/lista", user=user_sesion), 
                area_principal
            ], expand=True, spacing=0)
        ]

    # --- HELPERS ---
    def _build_stat_card(self, titulo, control_txt, icono, color):
        return ft.Container(
            content=ft.Row([
                ft.Column([ft.Text(titulo, size=11, color="#a1a1aa"), control_txt], spacing=0),
                ft.Icon(icono, color=color, size=22),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            bgcolor="transparent",
            border=ft.border.all(1, "#27272a"),
            border_radius=12,
            padding=ft.padding.symmetric(horizontal=15, vertical=10),
            expand=True,
        )
    
    def _crear_texto_copiable(self, texto, color="#a1a1aa", weight=ft.FontWeight.NORMAL):
        """
        Crea un CONTENEDOR (no DataCell) que al hacer clic copia el texto.
        """
        return ft.Container(
            content=ft.Text(
                texto, 
                color=color, 
                size=13, 
                weight=weight,
                max_lines=1, 
                overflow=ft.TextOverflow.ELLIPSIS
            ),
            tooltip="Click para copiar", # Usamos la propiedad tooltip del Container
            on_click=lambda e: self._accion_copiar(texto),
            ink=True, 
            border_radius=4,
            padding=ft.padding.symmetric(horizontal=5, vertical=2)
        )

    def _accion_copiar(self, texto):
        self.page.set_clipboard(texto)
        self.page.open(ft.SnackBar(
            content=ft.Text(f"Copiado: {texto}", color="white"),
            bgcolor="#22c55e", # Verde éxito
            duration=1000 # Dura solo 1 segundo
        ))

    def _build_filter_btn(self, texto, estado):
        return ft.TextButton(
            content=ft.Text(texto, size=12, weight="bold", color="white"),
            on_click=lambda _: self.controller.filtrar_por_estado(estado)
        )

    def obtener_avatar(self, nombre):
        iniciales = "".join([p[0] for p in nombre.split(" ")[:2]]).upper() if nombre else "??"
        return ft.Container(
            content=ft.Text(iniciales, size=10, weight="bold", color="white"),
            bgcolor="#3f3f46",
            width=32, height=32,
            border_radius=16,
            alignment=ft.alignment.center
        )

    def mostrar_socios(self, lista_socios, pagina_actual, total_paginas, total_socios=0, al_dia=0, con_deuda=0):
        # 1. Limpiamos y preparamos datos
        self.tabla.rows.clear()
        
        # Guardamos los valores en los controles (pero no actualizamos visualmente todavía)
        self.txt_total_socios.value = str(total_socios)
        self.txt_al_dia.value = str(al_dia)
        self.txt_con_deuda.value = str(con_deuda)
        self.txt_paginacion.value = f"{pagina_actual} / {max(1, total_paginas)}"
        
        self.btn_ant.disabled = (pagina_actual <= 1)
        self.btn_sig.disabled = (pagina_actual >= total_paginas)

        # 2. Llenamos las filas (Lógica de negocio)
        for socio in lista_socios:
            # --- Lógica de Badges ---
            est = socio.get('estado', '')
            act_raw = socio.get('actividad', '')
            act = act_raw.lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
            
            color_v = "#4ade80" if est == "AL_DIA" else "#f87171" if est == "VENCIDO" else "#a78bfa"
            
            badge_estado = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.icons.CIRCLE, color=color_v, size=8),
                    ft.Text(est.replace("_", " "), size=10, weight="bold", color=color_v),
                ], spacing=5, tight=True),
                bgcolor=ft.Colors.with_opacity(0.1, color_v),
                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                border_radius=6,
            )

            if "musculacion" in act and "body pump" in act:
                icon_act = ft.icons.HUB_ROUNDED; color_act = "#fbbf24"; txt_act = "Musculación + Pump"
            elif "body pump" in act:
                icon_act = ft.icons.BOLT_ROUNDED; color_act = "#f97316"; txt_act = "Body Pump"
            elif "musculacion" in act:
                icon_act = ft.icons.FITNESS_CENTER_ROUNDED; color_act = "#3b82f6"; txt_act = "Musculación"
            else:
                icon_act = ft.icons.HELP_OUTLINE_ROUNDED; color_act = "white24"; txt_act = act_raw if act_raw else "No asignada"

            badge_actividad = ft.Row([
                ft.Icon(icon_act, size=14, color=color_act),
                ft.Text(txt_act, size=12, color="white70")
            ], spacing=8)
            # ------------------------

            self.tabla.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Row([
                            self.obtener_avatar(socio.get('nombre', '')),
                            self._crear_texto_copiable(socio.get('nombre', 'Sin Nombre'), color="white", weight="bold")
                        ], spacing=10)),
                        ft.DataCell(self._crear_texto_copiable(str(socio.get('dni', '')))),
                        ft.DataCell(self._crear_texto_copiable(str(socio.get('telefono', '-')))),
                        ft.DataCell(badge_actividad),
                        ft.DataCell(ft.Text(socio.get('vencimiento_str', '---'), color="#a1a1aa", size=13)),
                        ft.DataCell(ft.Row([badge_estado], alignment=ft.MainAxisAlignment.START)),
                        ft.DataCell(ft.Row([
                            ft.IconButton(ft.icons.PAYMENT, icon_color="#22c55e", icon_size=18, tooltip="Pagos", on_click=lambda _, d=socio['dni']: self.page.go(f"/pagos?dni={d}")),
                            ft.IconButton(ft.icons.EDIT, icon_color="#3b82f6", icon_size=18, tooltip="Editar", on_click=lambda _, d=socio['dni']: self.page.go(f"/editar_socio?dni={d}")),
                            ft.IconButton(ft.icons.DELETE, icon_color="#ef4444", icon_size=18, tooltip="Eliminar", on_click=lambda _, s=socio: self.controller.solicitar_eliminacion(s['dni'], s['nombre'])),
                        ], spacing=0))
                    ]
                )
            )
        
        # 3. --- PROTECCIÓN CONTRA EL ERROR CRÍTICO ---
        # Solo hacemos update() si la tabla ya está efectivamente en la página.
        if self.tabla.page:
            self.tabla.update()
            self.txt_total_socios.update()
            self.txt_al_dia.update()
            self.txt_con_deuda.update()
            self.txt_paginacion.update()
            self.btn_ant.update()
            self.btn_sig.update()
        else:
            # Si no está en la página (primera carga), Flet pintará los datos 
            # automáticamente al terminar el __init__, no hace falta forzar update.
            pass

    def set_controller(self, ctrl):
        self.controller = ctrl

    def mostrar_dialogo_confirmacion(self, nombre, dni):
        self.dialogo = ft.AlertDialog(
            title=ft.Text("Eliminar Socio"),
            content=ft.Text(f"¿Estás seguro de eliminar a {nombre}?"),
            actions=[
                ft.TextButton("Cancelar", on_click=self.controller.cancelar_eliminacion),
                ft.TextButton("Eliminar", on_click=self.controller.confirmar_eliminacion, style=ft.ButtonStyle(color="red")),
            ]
        )
        self.page.open(self.dialogo)

    def cerrar_dialogo(self):
        if hasattr(self, 'dialogo'): self.page.close(self.dialogo)

    def mostrar_mensaje(self, msg, color="green"):
        self.page.open(ft.SnackBar(ft.Text(msg), bgcolor=color))