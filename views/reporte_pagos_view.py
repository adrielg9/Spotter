import flet as ft
from datetime import datetime
from views.sidebar_view import Sidebar

class ReportePagosView(ft.View):
    
    def __init__(self, page: ft.Page):
        super().__init__(route="/reporte_pagos")
        self.page = page
        self.controller = None
        
        # --- PALETA ---
        self.bg_main = "#050505"       
        self.bg_card = "#09090B"       
        self.border_color = "#27272A"  
        self.text_primary = "#F4F4F5"  
        self.text_secondary = "#A1A1AA"
        self.accent_color = "#6366f1"  
        self.c_red = "#ef4444"

        self.bgcolor = self.bg_main
        self.padding = 0
        
        # --- 1. CREAMOS LOS TEXTOS ---
        self.txt_total = ft.Text("$ 0", size=28, weight="bold", color="#4ade80", font_family="monospace")
        self.txt_efectivo = ft.Text("Efec: $ 0", size=12, color="#86efac") 
        self.txt_digital = ft.Text("Transf: $ 0", size=12, color="#60a5fa")

        # --- 2. TARJETA DE TOTALES ---
        self.card_total = ft.Container(
            content=ft.Column([
                ft.Text("TOTAL RECAUDADO", size=10, weight="bold", color=self.text_secondary),
                self.txt_total,
                ft.Row([self.txt_efectivo, self.txt_digital], spacing=10)
            ], spacing=2, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.END),
            padding=ft.padding.symmetric(horizontal=20, vertical=10),
            bgcolor=ft.Colors.with_opacity(0.05, "#4ade80"), 
            border=ft.border.all(1, "rgba(74, 222, 128, 0.2)"),
            border_radius=12
        )

        # --- FILTROS DE FECHA ---
        fecha_minima = datetime(2020, 1, 1)
        fecha_maxima = datetime(2050, 12, 31)

        self.date_picker_desde = ft.DatePicker(
            on_change=lambda e: self.controller.cambiar_fecha_desde(e),
            first_date=fecha_minima, last_date=fecha_maxima,
            date_picker_entry_mode=ft.DatePickerEntryMode.CALENDAR_ONLY,
            cancel_text="Cancelar", confirm_text="Seleccionar", help_text="Inicio"
        )
        
        self.date_picker_hasta = ft.DatePicker(
            on_change=lambda e: self.controller.cambiar_fecha_hasta(e),
            first_date=fecha_minima, last_date=fecha_maxima,
            date_picker_entry_mode=ft.DatePickerEntryMode.CALENDAR_ONLY,
            cancel_text="Cancelar", confirm_text="Seleccionar", help_text="Fin"
        )
        
        self.page.overlay.extend([self.date_picker_desde, self.date_picker_hasta])

        # Botones Filtros
        estilo_btn = ft.ButtonStyle(
            color=self.text_secondary, bgcolor="#18181B",
            shape=ft.RoundedRectangleBorder(radius=8), padding=15
        )
        self.btn_desde = ft.ElevatedButton("Desde", icon=ft.icons.CALENDAR_TODAY_OUTLINED, style=estilo_btn, on_click=lambda _: self.date_picker_desde.pick_date())
        self.btn_hasta = ft.ElevatedButton("Hasta", icon=ft.icons.CALENDAR_TODAY_OUTLINED, style=estilo_btn, on_click=lambda _: self.date_picker_hasta.pick_date())
        self.btn_limpiar = ft.IconButton(icon=ft.icons.FILTER_ALT_OFF, tooltip="Limpiar", icon_color="red", on_click=lambda e: self.controller.limpiar_filtros(e))

        # Buscador
        self.txt_buscar = ft.TextField(
            hint_text="Buscar socio...",
            hint_style=ft.TextStyle(color="#52525B", size=14),
            prefix_icon=ft.icons.SEARCH_ROUNDED,
            bgcolor="#18181B", border_width=1, border_color=self.border_color, border_radius=12,
            text_size=14, height=45, content_padding=10, expand=True,
            text_style=ft.TextStyle(color="white"), cursor_color="white", focused_border_color=self.accent_color,
            on_change=lambda e: self.controller.filtrar_por_nombre(e)
        )

        # --- TABLA ---
        self.tabla = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("FECHA", size=12, weight="bold", color=self.text_secondary)),
                ft.DataColumn(ft.Text("SOCIO", size=12, weight="bold", color=self.text_secondary)),
                ft.DataColumn(ft.Text("CONCEPTO", size=12, weight="bold", color=self.text_secondary)),
                ft.DataColumn(ft.Text("MÉTODO", size=12, weight="bold", color=self.text_secondary)), 
                ft.DataColumn(ft.Text("MONTO", size=12, weight="bold", color=self.text_secondary), numeric=True),
                ft.DataColumn(ft.Text("ACCION", size=12, weight="bold", color=self.text_secondary)),
            ],
            rows=[],
            border=ft.border.all(0, "transparent"), 
            heading_row_height=60, 
            data_row_min_height=60,
            heading_row_color=self.bg_card, 
            divider_thickness=1, 
            column_spacing=30
        )

        # --- CONTROLES DE PAGINACIÓN ---
        self.btn_anterior = ft.IconButton(
            icon=ft.icons.CHEVRON_LEFT_ROUNDED, 
            icon_color="white", 
            disabled=True,
            on_click=lambda _: self.controller.cambiar_pagina(-1)
        )
        self.btn_siguiente = ft.IconButton(
            icon=ft.icons.CHEVRON_RIGHT_ROUNDED, 
            icon_color="white", 
            disabled=True,
            on_click=lambda _: self.controller.cambiar_pagina(1)
        )
        self.txt_paginacion = ft.Text("Página 1 de 1", color=self.text_secondary, size=13)

        self.contenedor_paginacion = ft.Row(
            controls=[self.btn_anterior, self.txt_paginacion, self.btn_siguiente],
            alignment=ft.MainAxisAlignment.CENTER, 
            spacing=20
        )

        # --- CONTENIDO PRINCIPAL ---
        contenido = ft.Container(
            padding=ft.padding.all(40),
            expand=True,
            content=ft.Column([
                ft.Row([
                    ft.Row([
                        ft.Container(content=ft.Icon(ft.icons.MONETIZATION_ON_ROUNDED, color=self.accent_color, size=32), padding=10, bgcolor=ft.Colors.with_opacity(0.1, self.accent_color), border_radius=12),
                        ft.Column([
                            ft.Text("Reporte Financiero", size=24, weight="bold", color="white", font_family="Roboto"),
                            ft.Text("Haz clic en una fila para ver detalles", size=14, color=self.text_secondary),
                        ], spacing=2)
                    ]),
                    self.card_total
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                ft.Container(height=20),
                
                ft.Container(
                    padding=10, bgcolor=self.bg_card, border_radius=12, border=ft.border.all(1, self.border_color),
                    content=ft.Row([self.txt_buscar, ft.VerticalDivider(width=10, color="transparent"), self.btn_desde, self.btn_hasta, self.btn_limpiar], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                ),
                
                ft.Container(height=10),
                
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row([self.tabla], scroll=ft.ScrollMode.AUTO) 
                        ], 
                        scroll=ft.ScrollMode.AUTO, 
                    ),
                    expand=True, 
                    bgcolor=self.bg_card, 
                    border=ft.border.all(1, self.border_color),
                    border_radius=16, 
                    shadow=ft.BoxShadow(blur_radius=20, color=ft.Colors.with_opacity(0.05, "white")),
                    padding=ft.padding.only(bottom=10),
                    alignment=ft.alignment.top_center,
                    margin=ft.margin.symmetric(horizontal=20) 
                ),

                ft.Container(height=10),
                self.contenedor_paginacion 
            ])
        )

        user_actual = self.page.session.get("user") or "Usuario"
        self.controls = [ft.Row([Sidebar(self.page, "/reporte_pagos", user=user_actual), contenido], expand=True, spacing=0)]

    def set_controller(self, ctrl):
        self.controller = ctrl
        self.controller.cargar_datos()

    # --- UI UPDATES ---
    def actualizar_contadores(self, general, efectivo, digital):
        gen_fmt = f"{general:,.0f}".replace(",", ".")
        efec_fmt = f"{efectivo:,.0f}".replace(",", ".")
        dig_fmt = f"{digital:,.0f}".replace(",", ".")

        self.txt_total.value = f"$ {gen_fmt}"
        self.txt_efectivo.value = f"Efec: ${efec_fmt}"
        self.txt_digital.value = f"Transf: ${dig_fmt}"
        
        if self.txt_total.page:
            self.txt_total.update()
            self.txt_efectivo.update()
            self.txt_digital.update()

    def actualizar_paginacion_ui(self, pag_actual, total_pags):
        self.txt_paginacion.value = f"Página {pag_actual} de {max(1, total_pags)}"
        self.btn_anterior.disabled = (pag_actual <= 1)
        self.btn_siguiente.disabled = (pag_actual >= total_pags)
        
        if self.contenedor_paginacion.page:
            self.contenedor_paginacion.update()

    # --- DIÁLOGO DE CONFIRMACIÓN (CORREGIDO) ---
    def confirmar_eliminacion(self, id_pago):
        def proceder(e):
            # 1. CERRAMOS EL DIÁLOGO EXPLÍCITAMENTE
            self.page.close(dlg) 
            
            # 2. Ejecutamos lógica
            exito = self.controller.borrar_pago(id_pago)
            
            # 3. Mostramos feedback
            msg = "Pago eliminado correctamente" if exito else "Error al eliminar el pago"
            color = "green" if exito else "red"
            self.page.open(ft.SnackBar(ft.Text(msg, color="white"), bgcolor=color))

        def cancelar(e):
            # CERRAMOS EL DIÁLOGO EXPLÍCITAMENTE
            self.page.close(dlg)

        dlg = ft.AlertDialog(
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text("¿Estás seguro de que deseas eliminar este registro de pago?\nEsta acción es irreversible."),
            actions=[
                ft.TextButton("Cancelar", on_click=cancelar),
                ft.TextButton("Eliminar", on_click=proceder, style=ft.ButtonStyle(color=self.c_red)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            modal=True
        )
        self.page.open(dlg)

    # --- DETALLES (CORREGIDO) ---
    def mostrar_detalle(self, pago):
        quien_cobro = pago.get("usuario") or "Desconocido"
        fecha_raw = str(pago.get("fecha_pago"))
        hora_only = "--:--"
        try:
            dt_obj = datetime.strptime(fecha_raw, "%Y-%m-%d %H:%M:%S")
            hora_only = dt_obj.strftime("%H:%M")
        except:
            if len(fecha_raw) >= 16: hora_only = fecha_raw[11:16]
            else: hora_only = "00:00"

        monto_val = pago['monto']
        monto_fmt = f"{monto_val:,.0f}".replace(",", ".")

        content = ft.Container(
            width=420, padding=20,
            content=ft.Column([
                self._crear_item_detalle("Socio", pago['nombre_completo'], ft.icons.PERSON_ROUNDED),
                ft.Divider(color=self.border_color, height=20),
                self._crear_item_detalle("Monto Cobrado", f"${monto_fmt}", ft.icons.ATTACH_MONEY_ROUNDED, color_texto="#4ade80", size_texto=24),
                ft.Divider(color=self.border_color, height=20),
                self._crear_item_detalle("Método de Pago", pago.get('metodo_pago') or "-", ft.icons.CREDIT_CARD_ROUNDED),
                ft.Divider(color=self.border_color, height=20),
                ft.Container(
                    bgcolor="#27272A", padding=15, border_radius=10,
                    content=ft.Column([
                        self._crear_item_detalle("Cobrado por", quien_cobro.upper(), ft.icons.ADMIN_PANEL_SETTINGS_ROUNDED, color_texto=self.accent_color),
                        ft.Container(height=10),
                        self._crear_item_detalle("Hora exacta", hora_only + " hs", ft.icons.ACCESS_TIME_FILLED_ROUNDED),
                    ])
                )
            ], spacing=0, tight=True)
        )
        
        # Función interna para cerrar este diálogo específico
        def cerrar_detalle(e):
            self.page.close(dlg)

        dlg = ft.AlertDialog(
            title=ft.Text("Detalle de Transacción", weight="bold", size=22, font_family="Roboto"),
            content=content, bgcolor="#18181B", shape=ft.RoundedRectangleBorder(radius=16),
            actions=[ft.TextButton(content=ft.Text("Cerrar", size=16), on_click=cerrar_detalle, style=ft.ButtonStyle(color="white"))],
            actions_alignment=ft.MainAxisAlignment.END, actions_padding=20
        )
        self.page.open(dlg)

    def _crear_item_detalle(self, label, valor, icono, color_texto="white", size_texto=18):
        return ft.Row([
            ft.Container(content=ft.Icon(icono, size=28, color=self.text_secondary), padding=10, bgcolor=ft.Colors.with_opacity(0.05, "white"), border_radius=10),
            ft.Column([ft.Text(label, size=13, color=self.text_secondary), ft.Text(valor, size=size_texto, weight="bold", color=color_texto, font_family="Roboto")], spacing=2)
        ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER)

    def _crear_badge_metodo(self, metodo_raw):
        texto_bd = (metodo_raw or "OTRO").upper()
        estilos = {
            "EFECTIVO": {"bg": "rgba(20, 83, 45, 0.6)", "txt": "#4ade80", "borde": "#22c55e"},
            "TRANSFERENCIA": {"bg": "rgba(8, 47, 73, 0.6)", "txt": "#38BDF8", "borde": "#0EA5E9"},
            "DEFAULT": {"bg": "#27272A", "txt": "#ffffff", "borde": "#52525b"}
        }
        if "EFECTIVO" in texto_bd: estilo = estilos["EFECTIVO"]; texto_mostrar = "EFECTIVO"
        elif any(x in texto_bd for x in ["TRANSF", "MP", "MERCADO", "DIGITAL"]): estilo = estilos["TRANSFERENCIA"]; texto_mostrar = "TRANSFERENCIA"
        else: estilo = estilos["DEFAULT"]; texto_mostrar = texto_bd

        return ft.Container(
            content=ft.Text(texto_mostrar, size=12, weight=ft.FontWeight.W_900, color=estilo["txt"], font_family="Roboto"),
            bgcolor=estilo["bg"], height=40, width=110, padding=0, alignment=ft.alignment.center,
            border_radius=6, border=ft.border.all(1, estilo["borde"]),
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=2, color=ft.Colors.with_opacity(0.1, estilo["borde"]), offset=ft.Offset(0, 1))
        )

    def llenar_tabla(self, datos):
        self.tabla.rows.clear()
        for p in datos:
            monto = float(p['monto'])
            monto_fmt = f"{monto:,.0f}".replace(",", ".")
            fecha_raw = str(p['fecha_pago'])
            try:
                dt_obj = datetime.strptime(fecha_raw, "%Y-%m-%d %H:%M:%S")
                fecha_fmt = dt_obj.strftime("%d-%m-%Y") 
                hora_fmt = dt_obj.strftime("%H:%M")
            except:
                fecha_fmt = fecha_raw
                hora_fmt = ""

            metodo = p.get('metodo_pago')
            id_pago = p.get('id')

            btn_eliminar = ft.IconButton(
                icon=ft.icons.DELETE_OUTLINE_ROUNDED,
                icon_color=self.c_red,
                tooltip="Eliminar registro",
                on_click=lambda e, x=id_pago: self.confirmar_eliminacion(x)
            )
            
            self.tabla.rows.append(ft.DataRow(
                on_select_changed=lambda e, p=p: self.mostrar_detalle(p), 
                cells=[
                    ft.DataCell(ft.Column([ft.Text(fecha_fmt, color="white", size=13, weight="bold"), ft.Text(hora_fmt, color=self.text_secondary, size=11)], alignment=ft.MainAxisAlignment.CENTER, spacing=2)), 
                    ft.DataCell(ft.Row([ft.Container(content=ft.Text(p['nombre_completo'][0].upper(), color="black", weight="bold", size=12), width=28, height=28, bgcolor="white", border_radius=14, alignment=ft.alignment.center), ft.Text(p['nombre_completo'], weight="w500", color=self.text_primary)], spacing=10)), 
                    ft.DataCell(ft.Text(p['concepto'], color=self.text_secondary, size=13)), 
                    ft.DataCell(self._crear_badge_metodo(metodo)), 
                    ft.DataCell(ft.Text(f"${monto_fmt}", color="#4ADE80", weight="bold", size=17, font_family="monospace")),
                    ft.DataCell(btn_eliminar),
                ]
            ))
        
        if self.tabla.page:
            self.tabla.update()