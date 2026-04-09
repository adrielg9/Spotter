import urllib.parse 

class PagoCtrl:
    def __init__(self, view, admin_service, checkin_service):
        self.view = view
        self.admin_service = admin_service
        self.checkin_service = checkin_service

        self.socios_maestros = []
        self.origen = "/home"

    def cargar_datos(self):
        try:
            self.socios_maestros = self.admin_service.socio_repo.obtener_todos()
            parsed_url = urllib.parse.urlparse(self.view.page.route)
            params = urllib.parse.parse_qs(parsed_url.query)
            
            if 'origen' in params:
                valor_origen = params['origen'][0]
                
                # --- CORRECCIÓN DE SEGURIDAD ---
                # Si el origen es "/" (Login) o está vacío, forzamos ir al Home
                # para evitar que el usuario sea expulsado al cancelar.
                if valor_origen == "/" or not valor_origen:
                    self.origen = "/home"
                else:
                    self.origen = valor_origen
            
            if 'dni' in params:
                dni_buscado = params['dni'][0]
                socio = next((s for s in self.socios_maestros if str(s['dni']) == dni_buscado), None)
                if socio:
                    self.seleccionar_socio(socio)
        except Exception as e:
            print(f"Error en carga de pagos: {e}")

    def filtrar_sugerencias(self, e):
        texto = e.control.value.lower()
        if len(texto) < 2:
            self.view.mostrar_sugerencias([])
            return
        filtrados = [
            s for s in self.socios_maestros 
            if texto in s['nombre'].lower() or texto in str(s['dni'])
        ]
        self.view.mostrar_sugerencias(filtrados[:5])

    def seleccionar_socio(self, socio):
        self.view.preparar_formulario_pago(socio)

    def registrar_pago(self, e):
        try:
            dni = self.view.txt_busqueda.value
            if not self.view.txt_monto.value:
                self.view.mostrar_mensaje("Ingrese un monto", color="red")
                return
            monto = float(self.view.txt_monto.value)
            
            actividad = self.view.dd_actividad.value
            if not actividad:
                self.view.mostrar_mensaje("Seleccione una actividad", color="red")
                return
            
            metodo = self.view.dd_metodo.value
            if not metodo:
                self.view.mostrar_mensaje("Seleccione un método de pago", color="red")
                return

            # --- CAPTURAMOS EL USUARIO ---
            usuario_actual = self.view.page.session.get("user") or "Sistema"
            usuario_actual = self.view.page.session.get("user") or "Sistema"
            print(f"DEBUG: Registrando pago con usuario: {usuario_actual}") # Para ver en consola
            # Llamamos al servicio con la actividad. Duración fija de 1 mes (30 días).
            nueva_fecha = self.checkin_service.renovar_cuota(dni, 1, monto, actividad, metodo, usuario=usuario_actual)         
               
            self.view.mostrar_mensaje(f"¡Pago de {actividad} registrado! Vence: {nueva_fecha}")
            self.view.limpiar_todo()
            self.view.page.go(self.origen)
            
        except Exception as ex:
            self.view.mostrar_mensaje(f"Error al pagar: {ex}", color="red")

    def cancelar(self, e):
        self.view.limpiar_todo()