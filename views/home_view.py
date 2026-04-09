import flet as ft
from datetime import datetime
from views.sidebar_view import Sidebar

class HomeView(ft.View):
    def __init__(self, page):
        super().__init__(route="/home")
        self.page = page
        self.controller = None 
        
        self.usuario_sesion = self.page.session.get("user") or "Usuario"
                
        # --- CONFIGURACIÓN BASE ---
        self.padding = 0
        self.bgcolor = "#09090B"
        self.expand = True       
        
        # --- PALETA ---
        self.c_blue = "#3B82F6"; self.c_green = "#22C55E"; self.c_purple = "#A855F7"
        self.c_orange = "#F97316"; self.c_red = "#EF4444"; self.c_muted = "#A1A1AA"; self.c_border = "#27272A"

        # --- VARIABLES DE DATOS (KPIs) ---
        self.txt_total_alumnos = ft.Text("0", size=30, weight="bold", color="white")
        self.txt_sub_alumnos = ft.Text("Cargando...", size=14, color=self.c_muted)
        
        # Tarjeta Verde: Nuevos Socios (Altas)
        self.txt_altas = ft.Text("0", size=30, weight="bold", color="white")
        
        self.txt_al_dia = ft.Text("0", size=30, weight="bold", color="white")
        self.txt_con_deuda = ft.Text("0 con deuda", size=14, color=self.c_muted)
        self.txt_asistencias = ft.Text("0", size=30, weight="bold", color="white")
        
        # --- LISTAS CENTRALES ---
        self.col_lista_pagos = ft.Column(spacing=0)
        self.col_lista_asistencias = ft.Column(spacing=0) 
        
        # --- CONSTRUCCIÓN DEL LAYOUT ---

        # 1. HEADER
        header = ft.Container(
            content=ft.Column([
                ft.Text(f"DASHBOARD", size=28, weight="bold", color="white"), 
                ft.Text("Vista general del gimnasio", size=14, color=self.c_muted)
            ], spacing=4), 
            margin=ft.margin.only(bottom=24) 
        )

        # 2. KPI GRID (Tarjetas Superiores)
        kpi_grid = ft.ResponsiveRow(
            columns=12, spacing=16, run_spacing=16,
            controls=[
                self._crear_kpi_wrapper("ALUMNOS", self.txt_total_alumnos, self.txt_sub_alumnos, ft.icons.PEOPLE, self.c_blue),
                self._crear_kpi_wrapper("NUEVOS SOCIOS", self.txt_altas, ft.Text("Este mes", size=14, color=self.c_muted), ft.icons.PERSON_ADD, self.c_green),
                self._crear_kpi_wrapper("AL DÍA", self.txt_al_dia, self.txt_con_deuda, ft.icons.CHECK_CIRCLE, self.c_purple),
                self._crear_kpi_wrapper("ASISTENCIAS HOY", self.txt_asistencias, ft.Text("Registradas hoy", size=14, color=self.c_muted), ft.icons.ACCESS_TIME_FILLED, self.c_orange),
            ]
        )
        seccion_kpis = ft.Container(content=kpi_grid, margin=ft.margin.only(bottom=24))

        # 3. SECCIÓN CENTRAL (Dos columnas)
        
        # --- TARJETA IZQUIERDA: ÚLTIMOS ACCESOS ---
        card_asistencias = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.icons.DIRECTIONS_RUN, color=self.c_orange, size=20), 
                    ft.Text("Últimas asistencias", weight="bold", size=16, color="white")
                ], spacing=8),
                ft.Container(height=16),
                self.col_lista_asistencias
            ], spacing=0),
            bgcolor="#09090B", border=ft.border.all(1, self.c_border), border_radius=8, padding=24, col={"sm": 12, "lg": 6}
        )

        # --- TARJETA DERECHA: ÚLTIMOS PAGOS ---
        card_pagos = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.icons.MONETIZATION_ON_OUTLINED, color=self.c_green, size=20), 
                    ft.Text("Últimos Pagos", weight="bold", size=16, color="white")
                ], spacing=8),
                ft.Container(height=16),
                self.col_lista_pagos 
            ], spacing=0),
            bgcolor="#09090B", border=ft.border.all(1, self.c_border), border_radius=8, padding=24, col={"sm": 12, "lg": 6}
        )

        seccion_central = ft.ResponsiveRow(columns=12, spacing=24, run_spacing=24, controls=[card_asistencias, card_pagos])
        contenedor_central = ft.Container(content=seccion_central, margin=ft.margin.only(bottom=24))

        # LAYOUT FINAL
        # Nota: La alineación 'START' dentro de la columna evita que baje al maximizar
        area_principal = ft.Container(
            content=ft.Column(
                controls=[header, seccion_kpis, contenedor_central], 
                scroll=ft.ScrollMode.AUTO,
                alignment=ft.MainAxisAlignment.START, 
                spacing=20
            ),
            expand=True, 
            padding=ft.padding.only(top=20, left=40, right=40, bottom=40),
            bgcolor="#09090B"
        )
        
        self.controls = [
            ft.Row(
                controls=[
                    Sidebar(self.page, "/home", user=self.usuario_sesion), 
                    area_principal
                ], 
                expand=True, 
                spacing=0,
                vertical_alignment=ft.CrossAxisAlignment.START 
            )
        ]

    def set_controller(self, controller):
        self.controller = controller
        # El controlador cargará los datos después de instanciarse

    def actualizar_datos(self, datos):
        """Recibe el diccionario del Repositorio y pinta la pantalla"""
        
        # 1. KPIs Generales
        self.txt_total_alumnos.value = str(datos.get("socios_total") or 0)
        self.txt_sub_alumnos.value = f"Activos: {datos.get('socios_al_dia') or 0}"
        
        self.txt_altas.value = str(datos.get("altas_mes") or 0)
        
        self.txt_al_dia.value = str(datos.get("socios_al_dia") or 0)
        self.txt_con_deuda.value = f"{datos.get('socios_deuda') or 0} con deuda"
        
        self.txt_asistencias.value = str(datos.get("asistencias_hoy") or 0)
        
        # 2. LISTA DERECHA: Últimos Pagos
        self.col_lista_pagos.controls.clear()
        pagos = datos.get("ultimos_pagos")
        
        if not pagos:
            self._agregar_mensaje_vacio(self.col_lista_pagos, "Sin pagos recientes")
        else:
            for p in pagos:
                # --- A. FORMATO FECHA (DD/MM/YYYY) ---
                fecha_raw = str(p.get('fecha_vencimiento', ''))
                fecha_fmt = fecha_raw 
                try:
                    fecha_clean = fecha_raw[:10]
                    dt_obj = datetime.strptime(fecha_clean, "%Y-%m-%d")
                    fecha_fmt = dt_obj.strftime("%d/%m/%Y") # Barras en vez de guiones
                except:
                    fecha_fmt = fecha_raw.replace("-", "/")

                # --- B. FORMATO MONEDA (Con Punto de mil) ---
                # 1. Obtenemos el numero float
                monto_val = float(p.get('monto') or 0)
                # 2. Formateamos con coma (ingles): 1,500
                monto_str = f"{monto_val:,.0f}"
                # 3. Reemplazamos coma por punto: 1.500
                monto_final = monto_str.replace(",", ".")
                
                fila = self._crear_fila_lista(
                    titulo=p.get('nombre', 'Desconocido'),
                    subtitulo=f"Vence: {fecha_fmt}", 
                    valor=f"${monto_final}", # Usamos el monto con puntos
                    color_valor=self.c_green,
                    icono=ft.icons.ATTACH_MONEY
                )
                self.col_lista_pagos.controls.append(fila)

        # 3. LISTA IZQUIERDA: Últimas Asistencias
        self.col_lista_asistencias.controls.clear()
        asistencias = datos.get("ultimas_asistencias")
        
        if not asistencias:
            self._agregar_mensaje_vacio(self.col_lista_asistencias, "Nadie ha ingresado aún")
        else:
            for a in asistencias:
                # a es un diccionario: {'nombre': ..., 'hora': ...}
                fecha_raw = str(a.get('hora', ''))
                hora_fmt = "--:--"
                
                # Intentamos parsear la hora
                try:
                    dt = datetime.strptime(fecha_raw, "%Y-%m-%d %H:%M:%S.%f")
                    hora_fmt = dt.strftime("%H:%M")
                except:
                    try:
                        dt = datetime.strptime(fecha_raw, "%Y-%m-%d %H:%M:%S")
                        hora_fmt = dt.strftime("%H:%M")
                    except:
                        # Fallback simple
                        if len(fecha_raw) > 10: hora_fmt = fecha_raw[11:16]

                fila = self._crear_fila_lista(
                    titulo=a.get('nombre', 'Socio'),
                    subtitulo="Acceso permitido",
                    valor=f"{hora_fmt} hs",
                    color_valor=self.c_muted,
                    icono=ft.icons.PERSON_ROUNDED
                )
                self.col_lista_asistencias.controls.append(fila)

    # --- HELPERS DE DISEÑO ---
    
    def _crear_fila_lista(self, titulo, subtitulo, valor, color_valor, icono):
        """Crea una fila estandarizada para listas"""
        return ft.Container(
            content=ft.Row([
                ft.Row([
                    ft.Container(
                        content=ft.Icon(icono, size=18, color=self.c_muted),
                        bgcolor=ft.Colors.with_opacity(0.1, self.c_border),
                        padding=8, border_radius=8
                    ),
                    ft.Column([
                        ft.Text(titulo, color="white", weight="bold", size=14),
                        ft.Text(subtitulo, color=self.c_muted, size=12)
                    ], spacing=2)
                ]),
                ft.Text(valor, color=color_valor, weight="bold", size=14)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.symmetric(vertical=12),
            border=ft.border.only(bottom=ft.border.BorderSide(1, self.c_border))
        )

    def _agregar_mensaje_vacio(self, columna, mensaje):
        columna.controls.append(
            ft.Container(
                content=ft.Text(mensaje, color=self.c_muted, size=14, text_align="center"),
                padding=20, alignment=ft.alignment.center
            )
        )

    def _crear_kpi_wrapper(self, titulo, control_valor, control_sub, icono, color_base):
        content = ft.Container(content=ft.Column([ft.Row([ft.Container(content=ft.Icon(icono, color="white", size=24), bgcolor=color_base, width=48, height=48, border_radius=8, alignment=ft.alignment.center), ft.Container(expand=True), ft.Text(titulo, color=color_base, size=12, weight="bold")], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.START), ft.Container(height=16), control_valor, ft.Container(content=control_sub, margin=ft.margin.only(top=4))], spacing=0), gradient=ft.LinearGradient(begin=ft.alignment.top_left, end=ft.alignment.bottom_right, colors=[ft.Colors.with_opacity(0.1, color_base), ft.Colors.with_opacity(0.05, color_base)]), border=ft.border.all(1, ft.Colors.with_opacity(0.3, color_base)), border_radius=8, padding=24)
        return ft.Container(content=content, col={"xs": 12, "md": 6, "lg": 3})