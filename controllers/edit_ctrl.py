import urllib.parse
import time
# IMPORTANTE: Importamos el nuevo esquema 👇
from schemas import EdicionSocioInput 
from pydantic import ValidationError # <--- 1. IMPORTANTE: Agregar esto

class EditSocioCtrl:
    def __init__(self, view, service):
        self.view = view
        self.service = service
        self.dni_actual = None

    def cargar_datos_edicion(self):
        try:
            parsed_url = urllib.parse.urlparse(self.view.page.route)
            params = urllib.parse.parse_qs(parsed_url.query)
            
            if 'dni' in params:
                self.dni_actual = params['dni'][0]
                socio = self.service.buscar_por_dni(self.dni_actual)
                if socio:
                    self.view.rellenar_datos(socio)
            else:
                self.view.mostrar_mensaje("Error: No se especificó un socio", "red")
        except Exception as e:
            print(f"Error carga: {e}")

    def actualizar_socio(self, e):
        try:
            # 1. Obtenemos datos limpios de la vista
            nuevo_nombre = self.view.txt_nombre.value.strip()
            nuevo_tel = self.view.txt_tel.value.strip()
            
            # Validación manual rápida (opcional, pero recomendada)
            if not nuevo_nombre or not nuevo_tel:
                self.view.mostrar_mensaje("Complete todos los campos", "red")
                return

            # 2. VALIDACIÓN PYDANTIC
            # Aquí es donde salta el error si los datos no cumplen las reglas
            usuario_valido = EdicionSocioInput(
                dni=self.dni_actual,
                nombre=nuevo_nombre,
                telefono=nuevo_tel
            )

            # 3. Llamamos al servicio
            self.service.actualizar_datos_socio(
                dni=self.dni_actual,
                nombre=usuario_valido.nombre,
                telefono=usuario_valido.telefono
            )
            
            self.view.mostrar_mensaje("¡Socio actualizado correctamente!", "green")
            self.view.update() # Aseguramos refresco visual
            time.sleep(1.5)
            self.view.page.go("/lista")
            
        except ValidationError as e:
            # --- AQUÍ ESTÁ LA MAGIA ---
            # Recorremos la lista de errores que nos da Pydantic
            mensajes_limpios = []
            
            for error in e.errors():
                # error['msg'] suele venir como "Value error, Nombre muy corto."
                # Lo limpiamos quitando "Value error, "
                msg_limpio = error['msg'].replace("Value error, ", "")
                mensajes_limpios.append(f"• {msg_limpio}")
            
            # Unimos todo con saltos de línea
            texto_final = "\n".join(mensajes_limpios)
            
            self.view.mostrar_mensaje(texto_final, "red")

        except Exception as ex:
            print(f"Error critico: {ex}")
            self.view.mostrar_mensaje("Error técnico al actualizar", "red")