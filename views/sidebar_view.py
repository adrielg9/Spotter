import flet as ft
from utils.audit_logger import AuditLogger # <--- Importar esto
from utils.logo import build_logo

class Sidebar(ft.Container):
    def __init__(self, page, route_actual, user="Usuario"):
        super().__init__()
        self.page = page
        self.route_actual = route_actual
        self.user = user
        
        # Configuración del Contenedor Sidebar
        self.width = 250
        self.bgcolor = "#050505" 
        self.padding = 30
        self.border = ft.border.only(right=ft.border.BorderSide(1, "#27272A"))
        self.alignment = ft.alignment.top_left
        
        # Colores
        self.c_blue = "#3B82F6"

        # Contenido
        self.content = ft.Column([
            # 1. Logo y Bienvenida
            ft.Container(
                content=ft.Column([
                   build_logo(),
                    ft.Container(height=5), # Espacio mínimo entre logo y nombre
                    ft.Text(f"Bienvenido, {self.user}", size=16, color="#A1A1AA", weight="bold"),
        
                    # --- LÍNEA DIVISORIA CON ESPACIADO ---
                    # Aumenta 'height' para separar más del menú de abajo
                    ft.Divider(height=40, color="#27272A", thickness=1),
                ], spacing=0),
                padding=ft.padding.only(bottom=30)
            ),
            
            # 2. Menú Principal
            self._crear_item("Dashboard", ft.icons.DASHBOARD_ROUNDED, "/home"),
            self._crear_item("Registrar Alumno", ft.icons.PERSON_ADD_ALT_1_ROUNDED, "/registro"),
            self._crear_item("Alumnos", ft.icons.PEOPLE_ALT_ROUNDED, "/lista"),
            self._crear_item("Actualizar Pagos", ft.icons.CREDIT_CARD, "/pagos?origen=/home"),
     

            *( [self._crear_item("Historial Accesos", ft.icons.HISTORY_EDU, "/reporte_accesos")] if self.user == "Diego" else [] ),
            *( [self._crear_item("Historial de pagos", ft.icons.MONETIZATION_ON, "/reporte_pagos")] if self.user == "Diego" else [] ),
            
            # Espaciador
            ft.Container(expand=True),
            
            # 3. Sección Inferior
            ft.Column([
                ft.Divider(color="#27272A", height=1),
                
                # --- BOTÓN ORIGINAL (ABAJO) ---
                # Mantenemos este botón aquí como estaba antes
                self._crear_item("Asistencia", ft.icons.CHECK_BOX_OUTLINED, "/checkin"),
                
                # Botón cerrar sesión
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.icons.LOGOUT_ROUNDED, color="#ef4444", size=20),
                        ft.Text("Cerrar Sesión", color="#ef4444", size=14)
                    ], spacing=15),
                    padding=ft.padding.symmetric(horizontal=15, vertical=12),
                    border_radius=8,
                    on_click=self._cerrar_sesion, # <--- Llamamos a una función nuestra
                    ink=True
                ),             
                ft.Container(height=10),
                # Créditos
                ft.Container(
                    content=ft.Text(
                        "Desarrollado por DuoStack DEVs © 2026 ",
                        size=14,
                        color="white",
                    ),
                    alignment=ft.alignment.center_left
                )
            ], spacing=5)
            
        ], spacing=5, expand=True)

    def _crear_item(self, texto, icono, ruta, color_custom=None):
        # Lógica de "Está Activo?"
        activo = self.route_actual.split("?")[0] == ruta.split("?")[0]
        
        if activo:
            bg_gradient = ft.LinearGradient(colors=[self.c_blue, "#2563EB"])
            color_text = "white"
            weight = "bold"
        else:
            bg_gradient = None
            color_text = color_custom if color_custom else "#A1A1AA"
            weight = "normal"
        
        return ft.Container(
            content=ft.Row([
                ft.Icon(icono, color=color_text, size=20),
                ft.Text(texto, color=color_text, weight=weight, size=14)
            ], spacing=15),
            padding=ft.padding.symmetric(horizontal=15, vertical=12),
            gradient=bg_gradient,
            bgcolor=ft.Colors.TRANSPARENT if not activo else None,
            border_radius=8,
            on_click=lambda _: self.page.go(ruta),
            ink=True
        )
    
    def _cerrar_sesion(self, e):
        """Registra la salida y navega al login"""
        
        # 1. Recuperamos el ID de la sesión
        id_sesion = self.page.session.get("session_id")
        
        # 2. Registramos la hora de salida en el JSON
        if id_sesion:
            logger = AuditLogger()
            logger.registrar_salida(id_sesion)
            
        # 3. Limpiamos sesión y nos vamos
        self.page.session.clear()
        self.page.go("/")