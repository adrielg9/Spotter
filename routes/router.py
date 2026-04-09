# --- 1. IMPORTS DE DATOS Y REPOSITORIOS ---
from data.db_context import DatabaseContext
from repositories.socio_repo import SocioRepository
from repositories.cobros_repo import CobrosRepository
from repositories.asistencia_repo import AsistenciaRepository
from repositories.usuario_repo import UsuarioRepository 

# --- 2. IMPORTS DE SERVICIOS (LÓGICA) ---
from services.registro_service import RegistroService
from services.checkin_service import CheckInService
from services.admin_service import AdminService
from services.auth_service import AuthService           

# --- 3. IMPORTS DE CONTROLADORES ---
from controllers.checkInCtrl import CheckInCtrl
from controllers.reg_ctrl import RegCtrl
from controllers.list_ctrl import ListaSociosCtrl
from controllers.pago_ctrl import PagoCtrl
from controllers.login_ctrl import LoginCtrl
from controllers.edit_ctrl import EditSocioCtrl
from controllers.profile_ctrl import ProfileCtrl
from controllers.home_ctrl import HomeCtrl
from controllers.reporte_pagos_ctrl import ReportePagosCtrl

# --- 4. IMPORTS DE VISTAS ---
from views.home_view import HomeView
from views.check_view import CheckInView
from views.reg_view import RegistroSocioView
from views.list_view import ListaSociosView
from views.pago_view import PagoView
from views.login_view import LoginView
from views.edit_view import EditarSocioView            
from views.reporte_accesos_view import ReporteAccesosView 

from views.reporte_pagos_view import ReportePagosView

class Router:
    def __init__(self, page, db_context):
        self.page = page
        self.db = db_context

    def route_change(self, route):
        # Limpiamos las vistas anteriores
        self.page.views.clear()

        # --- DIAGNÓSTICO DE SESIÓN ---
        usuario_actual = self.page.session.get("user")
        print(f"🔄 CAMBIO DE RUTA a {route.route}. Usuario en sesión: {usuario_actual}")
        # -----------------------------
        
        print(f"Navegando a: {route.route}")

        # ---------------------------------------------------------
        # RUTA: LOGIN (RAÍZ)
        # ---------------------------------------------------------
        if route.route == "/":
            repo_user = UsuarioRepository(self.db)
            service = AuthService(repo_user)
            
            view = LoginView(self.page)
            ctrl = LoginCtrl(view, service)
            
            # Verificamos cómo se asigna el controlador en tu LoginView
            if hasattr(view, 'set_controller'):
                view.set_controller(ctrl)
            else:
                view.controller = ctrl
            
            self.page.views.append(view)

        # ---------------------------------------------------------
        # RUTA: HOME (MENÚ PRINCIPAL)
        # ---------------------------------------------------------
        elif route.route == "/home":
            view = HomeView(self.page)
            
    
            ctrl = HomeCtrl(view, self.db)
            
            view.set_controller(ctrl)
            
        
            ctrl.cargar_dashboard()

            self.page.views.append(view)

        # ---------------------------------------------------------
        # RUTA: CHECK-IN 
        # ---------------------------------------------------------
        elif route.route == "/checkin":
            repo_socio = SocioRepository(self.db)
            repo_cobros = CobrosRepository(self.db)
            repo_asistencia = AsistenciaRepository(self.db)
            
            service = CheckInService(repo_socio, repo_cobros, repo_asistencia)
            view = CheckInView(self.page)
            ctrl = CheckInCtrl(view, service)
            view.controller = ctrl
            
            self.page.views.append(view)

        # ---------------------------------------------------------
        # RUTA: REGISTRO DE SOCIOS
        # ---------------------------------------------------------
        elif route.route.startswith("/registro"):
            repo_socio = SocioRepository(self.db)
            repo_cobros = CobrosRepository(self.db)
            
            service = RegistroService(repo_socio, repo_cobros)
            view = RegistroSocioView(self.page) 
            ctrl = RegCtrl(view, service) 
            view.controller = ctrl        
            
            # Tu controlador ya sabe extraer los datos de la URL
            ctrl.cargar_datos()

            self.page.views.append(view)
        # ---------------------------------------------------------
        # RUTA: LISTA DE SOCIOS
        # ---------------------------------------------------------
        elif route.route == "/lista":
            repo_socio = SocioRepository(self.db)
            repo_cobros = CobrosRepository(self.db)

            service = AdminService(repo_socio, repo_cobros)
            view = ListaSociosView(self.page)
            ctrl = ListaSociosCtrl(view, service)
            view.controller = ctrl

            # Cargar datos antes de mostrar la vista
            if hasattr(ctrl, 'cargar_datos'):
                ctrl.cargar_datos()

            self.page.views.append(view)

        # RUTA: PAGOS (CORREGIDA)
        # ---------------------------------------------------------
        elif route.route.startswith("/pagos"):
            repo_socio = SocioRepository(self.db)
            repo_cobros = CobrosRepository(self.db)
            repo_asis = AsistenciaRepository(self.db)
            
            svc_admin = AdminService(repo_socio, repo_cobros)
            svc_checkin = CheckInService(repo_socio, repo_cobros, repo_asis)
            
            view = PagoView(self.page)
            ctrl = PagoCtrl(view, svc_admin, svc_checkin) 
            view.controller = ctrl

            ctrl.cargar_datos()

            self.page.views.append(view)
        # ---------------------------------------------------------
        # RUTA: EDICIÓN (Con soporte para parámetros)
        # ---------------------------------------------------------
        elif route.route.startswith("/editar_socio"):  
            repo_socio = SocioRepository(self.db)
            repo_cobros = CobrosRepository(self.db)
            
            service = RegistroService(repo_socio, repo_cobros) 
            
            view = EditarSocioView(self.page)
            ctrl = EditSocioCtrl(view, service)
            
            if hasattr(view, 'set_controller'):
                view.set_controller(ctrl)
            else:
                view.controller = ctrl
            
            self.page.views.append(view)
        
        
        # --- AGREGAR ESTA RUTA NUEVA ---
        elif route.route == "/reporte_accesos":
            # Verificación de seguridad extra en el router
            usuario_actual = self.page.session.get("user")
            if usuario_actual == "Diego":
                self.page.views.append(ReporteAccesosView(self.page))
            else:
                self.page.go("/home") # Si no es Diego, lo devuelve al inicio
        
        elif route.route == "/reporte_pagos":
            user = self.page.session.get("user")
            if user == "Diego":
                # Instancias necesarias
                repo_cobros = CobrosRepository(self.db)
                
                view = ReportePagosView(self.page)
                ctrl = ReportePagosCtrl(view, repo_cobros)
                view.set_controller(ctrl)
                
                self.page.views.append(view)
            else:
                self.page.go("/home")


        self.page.update()