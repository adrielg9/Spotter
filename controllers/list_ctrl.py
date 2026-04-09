import math
import traceback

class ListaSociosCtrl:
    def __init__(self, view, service):
        self.view = view
        self.service = service
        
        # --- VARIABLES DE ESTADO ---
        self.lista_maestra = []   # Todos los socios de la BD
        self.lista_actual = []    # Los socios filtrados
        self.pagina_actual = 1
        self.items_por_pagina = 10 # Ajustado a 7 para que entre en tu pantalla
        self.dni_a_eliminar = None 

    def cargar_datos(self):
        try:
            # 1. Cargamos todo desde la BD una sola vez
            self.lista_maestra = self.service.obtener_padron_completo()
            self.lista_actual = self.lista_maestra # Al inicio, "actual" es todo
            self.pagina_actual = 1
            
            self.actualizar_vista()
        except Exception as e:
            print("\n❌ ERROR CRÍTICO EN LISTA:")
            traceback.print_exc()

    def filtrar_socios(self, texto):
        """
        Recibe el texto directamente desde la vista.
        Filtra la lista maestra y actualiza la vista.
        """
        texto = texto.lower() if texto else ""

        if not texto:
            self.lista_actual = self.lista_maestra
        else:
            # Filtramos sobre la maestra
            self.lista_actual = [
                s for s in self.lista_maestra
                if texto in s['nombre'].lower() or str(s['dni']).startswith(texto)
            ]

        # Reset a página 1 al buscar para ver los resultados desde el inicio
        self.pagina_actual = 1
        self.actualizar_vista()

    def filtrar_por_estado(self, estado):
        """
        Filtra la lista maestra por estado.
        """
        if estado == "TODOS":
            self.lista_actual = self.lista_maestra
        else:
            self.lista_actual = [
                s for s in self.lista_maestra
                if s.get('estado') == estado
            ]

        # Reset a página 1 al filtrar para ver los resultados desde el inicio
        self.pagina_actual = 1
        self.actualizar_vista()

    def cambiar_pagina(self, delta):
        """Maneja el clic de Anterior (-1) y Siguiente (+1)"""
        total_items = len(self.lista_actual)
        # math.ceil redondea hacia arriba (ej: 11 items / 10 = 1.1 -> 2 páginas)
        max_paginas = math.ceil(total_items / self.items_por_pagina)
        
        nueva_pagina = self.pagina_actual + delta
        
        # Validamos límites
        if 1 <= nueva_pagina <= max_paginas:
            self.pagina_actual = nueva_pagina
            self.actualizar_vista()

    def actualizar_vista(self):
        """Corta la lista y manda los datos a la vista"""
        total_items = len(self.lista_actual)

        # Calcular contadores
        total_socios = len(self.lista_maestra)
        al_dia = sum(1 for s in self.lista_maestra if s.get('estado') == 'AL_DIA')
        con_deuda = sum(1 for s in self.lista_maestra if s.get('estado') == 'VENCIDO')

        # Si no hay datos, mostramos vacío
        if total_items == 0:
            self.view.mostrar_socios([], 0, 0, total_socios, al_dia, con_deuda)
            return

        total_paginas = math.ceil(total_items / self.items_por_pagina)

        # Recorte de la lista (Slicing) para la paginación
        inicio = (self.pagina_actual - 1) * self.items_por_pagina
        fin = inicio + self.items_por_pagina
        datos_recortados = self.lista_actual[inicio:fin]

        # Enviamos los datos + info de paginación + contadores a la vista
        self.view.mostrar_socios(datos_recortados, self.pagina_actual, total_paginas, total_socios, al_dia, con_deuda)

    def solicitar_eliminacion(self, dni, nombre):
        self.dni_a_eliminar = dni
        self.view.mostrar_dialogo_confirmacion(nombre, dni)

    def confirmar_eliminacion(self, e):
        if self.dni_a_eliminar:
            try:
                self.service.eliminar_socio(self.dni_a_eliminar)
                self.view.cerrar_dialogo()
                self.view.mostrar_mensaje("Socio eliminado", color="green")
                self.cargar_datos() # Recargamos la lista actualizada
            except Exception as ex:
                self.view.cerrar_dialogo()
                self.view.mostrar_mensaje(f"Error: {ex}", color="red")
            self.dni_a_eliminar = None

    def cancelar_eliminacion(self, e):
        self.dni_a_eliminar = None
        self.view.cerrar_dialogo()