import math
from datetime import datetime

class ReportePagosCtrl:
    def __init__(self, view, cobros_repo):
        self.view = view
        self.repo = cobros_repo
        
        # --- 1. INICIALIZAMOS VARIABLES ---
        self.datos_totales = [] 
        
        # Filtros
        self.fecha_desde = None
        self.fecha_hasta = None

        # Paginación
        self.filtrados_cache = [] 
        self.pagina_actual = 1
        self.items_por_pagina = 10
        self.total_paginas = 1

        # --- 2. VINCULAMOS VISTA ---
        self.view.set_controller(self) 

    def cargar_datos(self):
        self.datos_totales = self.repo.obtener_historial_completo()
        self.aplicar_filtros()

    def cambiar_fecha_desde(self, e):
        if e.control.value:
            self.fecha_desde = e.control.value
            self.view.btn_desde.text = self.fecha_desde.strftime("%d-%m-%Y")
            self.view.btn_desde.update()
            self.aplicar_filtros()

    def cambiar_fecha_hasta(self, e):
        if e.control.value:
            self.fecha_hasta = e.control.value
            self.view.btn_hasta.text = self.fecha_hasta.strftime("%d-%m-%Y")
            self.view.btn_hasta.update()
            self.aplicar_filtros()

    def limpiar_filtros(self, e):
        self.fecha_desde = None
        self.fecha_hasta = None
        self.view.txt_buscar.value = ""
        
        self.view.btn_desde.text = "Desde"
        self.view.btn_hasta.text = "Hasta"
        
        self.view.update()
        self.aplicar_filtros()

    def filtrar_por_nombre(self, e):
        self.aplicar_filtros()

    def aplicar_filtros(self):
        texto = self.view.txt_buscar.value.lower() if self.view.txt_buscar.value else ""
        
        # 1. FILTRO DE FECHAS
        pagos_en_rango = []
        for pago in self.datos_totales:
            cumple_fecha = True
            
            if self.fecha_desde or self.fecha_hasta:
                try:
                    fecha_str = str(pago["fecha_pago"])[:10]
                    fecha_dt = datetime.strptime(fecha_str, "%Y-%m-%d")
                    
                    if self.fecha_desde and fecha_dt < self.fecha_desde:
                        cumple_fecha = False
                    
                    if self.fecha_hasta and fecha_dt > self.fecha_hasta:
                        cumple_fecha = False
                except:
                    pass 

            if cumple_fecha:
                pagos_en_rango.append(pago)

        # 2. LOGICA DE TOTALES
        total_general = 0
        total_efectivo = 0
        total_digital = 0

        tiene_rango_definido = (self.fecha_desde is not None) and (self.fecha_hasta is not None)

        if tiene_rango_definido:
            for p in pagos_en_rango:
                monto = float(p['monto'])
                metodo = (p.get('metodo_pago') or "").upper()
                
                if "EFECTIVO" in metodo:
                    total_efectivo += monto
                else:
                    total_digital += monto
            
            total_general = total_efectivo + total_digital
        
        self.view.actualizar_contadores(total_general, total_efectivo, total_digital)
        
        # 3. FILTRO DE TEXTO
        filtrados_final = []
        for p in pagos_en_rango:
            if not texto or texto in p["nombre_completo"].lower():
                filtrados_final.append(p)
        
        # 4. PAGINACIÓN
        self.filtrados_cache = filtrados_final
        self.pagina_actual = 1 
        self.actualizar_vista_paginada()

    def actualizar_vista_paginada(self):
        total_items = len(self.filtrados_cache)
        self.total_paginas = math.ceil(total_items / self.items_por_pagina)
        if self.total_paginas == 0: self.total_paginas = 1

        inicio = (self.pagina_actual - 1) * self.items_por_pagina
        fin = inicio + self.items_por_pagina
        
        items_a_mostrar = self.filtrados_cache[inicio:fin]
        
        self.view.llenar_tabla(items_a_mostrar)
        
        if hasattr(self.view, 'actualizar_paginacion_ui'):
            self.view.actualizar_paginacion_ui(self.pagina_actual, self.total_paginas)
        
        # --- SOLUCIÓN DEL ERROR ---
        # Verificamos 'uid'. Si es None, la vista no está montada todavía y no debemos hacer update.
        if self.view.uid is not None:
            self.view.update()

    def cambiar_pagina(self, delta):
        nueva_pag = self.pagina_actual + delta
        if 1 <= nueva_pag <= self.total_paginas:
            self.pagina_actual = nueva_pag
            self.actualizar_vista_paginada()
    
    # --- NUEVO MÉTODO PARA ELIMINAR ---
    def borrar_pago(self, id_pago):
        # 1. Llamamos al repo
        exito = self.repo.eliminar_pago(id_pago)
        
        # 2. Si se borró, recargamos los datos en memoria para actualizar la tabla
        if exito:
            self.cargar_datos() # Esto volverá a llamar a aplicar_filtros y refrescará la vista
            
        # 3. Retornamos el resultado para que la Vista decida qué mostrar (SnackBar verde o rojo)
        return exito