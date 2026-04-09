import threading
import flet as ft

class CheckInCtrl:
    def __init__(self, view, checkin_service):
        self.view = view
        self.service = checkin_service
        self.dni_actual = ""
        self.timer_limpieza = None

    def manejar_teclado(self, valor):
        if self.timer_limpieza:
            self.cancelar_timer()
            self.view.limpiar_resultado()

        if valor == "Limpiar":
            self.dni_actual = ""
        elif valor == "⌫": 
            self.dni_actual = self.dni_actual[:-1]
        else: 
            if len(self.dni_actual) < 8:
                self.dni_actual += valor
        
        self.view.actualizar_dni_display(self.dni_actual)

    def verificar_dni(self):
        if not self.dni_actual or len(self.dni_actual) < 7:
            return

        # 1. Bloqueamos el botón
        self.view.btn_verificar.disabled = True
        self.view.btn_verificar.update()

        try:
            resultado = self.service.registrar_ingreso(self.dni_actual)
            
            if resultado['estado'] == "AL_DIA":
                self.view.reproducir_sonido("exito")
                self.view.mostrar_resultado("success", resultado)
            
            elif resultado['estado'] == "YA_ASISTIO":
                self.view.reproducir_sonido("ya_asistio")
                resultado['mensaje_error'] = "Ya registró su ingreso hoy"
                self.view.mostrar_resultado("error", resultado)
            
            else:
                self.view.reproducir_sonido("vencido")
                resultado['mensaje_error'] = "Cuota Vencida o Pendiente"
                self.view.mostrar_resultado("error", resultado)

        except ValueError as e:
            if "no está registrado" in str(e):
                self.view.reproducir_sonido("no_existe")
                self.view.mostrar_resultado("not_found", self.dni_actual)
            else:
                self.view.reproducir_sonido("vencido")
                self.view.mostrar_resultado("error", {"nombre": "Error", "mensaje_error": str(e)})
        
        except Exception as e:
            print(f"Error crítico en controlador: {e}")
            self.view.mostrar_resultado("error", {"nombre": "Error Sistema", "mensaje_error": "Consulte al Técnico"})

        self.dni_actual = ""
        self.view.actualizar_dni_display(self.dni_actual)
        self.iniciar_timer_limpieza()

    def iniciar_timer_limpieza(self):
        self.cancelar_timer()
        self.timer_limpieza = threading.Timer(10.0, self.limpiar_todo)
        self.timer_limpieza.daemon = True 
        self.timer_limpieza.start()

    def cancelar_timer(self):
        if self.timer_limpieza:
            self.timer_limpieza.cancel()
            self.timer_limpieza = None

    def limpiar_todo(self):
        """Resetea la pantalla de resultados verificando si la vista sigue activa"""
        
        # --- CORRECCIÓN CRÍTICA ---
        # Verificamos si el botón principal de la vista aún tiene 'page'.
        # Si 'page' es None, significa que el usuario cambió de ruta y la vista fue removida.
        if not self.view.btn_verificar.page:
            # Si el usuario no está en CheckIn, abortamos la ejecución para no romper la app
            return 
        # ---------------------------

        try:
            # Reseteamos los valores de la vista
            self.view.limpiar_resultado()
            
            # Al limpiar después de los 7 segundos, el botón debe volver a estar apagado
            self.view.btn_verificar.disabled = True
            
            # Solo actualizamos si el control sigue vivo en la página
            if self.view.btn_verificar.page:
                self.view.btn_verificar.update()
                
        except Exception as e:
            # Si ocurre un error de 'Control not added to page' lo atrapamos aquí
            print(f"Limpieza ignorada: {e}")