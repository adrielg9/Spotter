import urllib.parse
from pydantic import ValidationError
from schemas import UsuarioInput
import time
import flet as ft

class RegCtrl:
    def __init__(self, view, service):
        self.view = view
        self.service = service
        self.dni_en_edicion = None
        self.view.page.on_keyboard_event = self.handle_keyboard

    def cargar_datos(self):
        try:
            parsed_url = urllib.parse.urlparse(self.view.page.route)
            params = urllib.parse.parse_qs(parsed_url.query)
            
            if 'dni' in params:
                dni_editar = params['dni'][0]
                self.dni_en_edicion = dni_editar 
                self.cargar_socio_para_editar(dni_editar)
            
            elif 'dni_nuevo' in params:
                self.dni_en_edicion = None 
                self.view.limpiar_formulario() 
                dni_nuevo = params['dni_nuevo'][0]
                self.view.txt_dni.value = dni_nuevo
                self.view.txt_nombre.focus()
                
        except Exception as e:
            print(f"DEBUG: Error cargando datos: {e}")

    def cargar_socio_para_editar(self, dni):
        try:
            socio = self.service.buscar_por_dni(dni)
            if socio:
                self.view.rellenar_formulario(socio)
                self.view.txt_dni.disabled = True  
                self.view.txt_dni.update() 
        except Exception as e:
            print(f"Error al buscar socio: {e}")

    def guardar_socio(self, e):
        # 1. Limpiamos errores previos
        self.view.limpiar_errores()
        
        datos = self.view.obtener_datos()
        errores = False

        # 2. VALIDACIÓN CON MENSAJES ESPECÍFICOS
        if not datos['nombre']:
            self.view.mostrar_error("nombre", "Campo requerido")
            errores = True
            
        if not datos['apellido']:
            self.view.mostrar_error("apellido", "Campo requerido")
            errores = True
            
        if not datos['dni']:
            self.view.mostrar_error("dni", "DNI requerido")
            errores = True
            
        if not datos['telefono']:
            self.view.mostrar_error("telefono", "Teléfono requerido")
            errores = True
            
        # El monto es obligatorio al crear
        if not self.dni_en_edicion and not datos['monto']:
            self.view.mostrar_error("monto", "Ingrese el monto inicial")
            errores = True

        if errores:
            # self.view.mostrar_mensaje("Verifique los campos en rojo", color="red") 
            # Opcional: ya no hace falta el snackbar si los campos hablan por sí mismos
            return

        # 3. PROCESO DE GUARDADO
        self.view.mostrar_loading()

        try:
            nombre_completo = f"{datos['nombre'].strip()} {datos['apellido'].strip()}".strip()
            
            usuario_valido = UsuarioInput(
                dni=datos['dni'],
                nombre=nombre_completo, 
                telefono=datos['telefono'],
            )

            if self.dni_en_edicion:
                self.service.actualizar_datos_socio(
                    dni=self.dni_en_edicion,
                    nombre=usuario_valido.nombre,
                    telefono=usuario_valido.telefono
                )
                self.view.mostrar_mensaje("Datos actualizados correctamente", color="green")
                time.sleep(0.5)
                self.view.page.go("/lista")

            else:
                monto = float(datos['monto'])
                usuario_actual = self.view.page.session.get("user") or "Sistema"
                self.service.registrar_socio(
                    dni=usuario_valido.dni,
                    nombre=usuario_valido.nombre,
                    telefono=usuario_valido.telefono,
                    monto=monto,
                    actividad=datos['actividad'],
                    metodo_pago=datos['metodo'],
                    usuario=usuario_actual 
                )
                self.view.mostrar_exito(usuario_valido.nombre)

        except ValidationError as e:
            msg = e.errors()[0]['msg'].replace('Value error, ', '')
            self.view.mostrar_mensaje(msg, color="orange")
        except ValueError as e:
            self.view.mostrar_mensaje(str(e), color="orange")
        except Exception as e:
            print(f"Error grave: {e}")
            self.view.mostrar_mensaje(f"Error: {e}", color="red")
        finally:
            self.view.ocultar_loading()

    def ir_al_inicio(self):
        self.view.page.go("/home")

    def reiniciar_registro(self):
        self.dni_en_edicion = None
        self.view.limpiar_formulario()

    def cancelar_formulario(self):
        if self.dni_en_edicion:
            self.view.page.go("/lista")
        else:
            self.view.page.go("/home")

    def handle_keyboard(self, e):
        if e.key == "S" and e.ctrl:
            if not self.view.is_loading:
                self.guardar_socio(None)
        elif e.key == "Escape":
            self.cancelar_formulario()