from datetime import datetime, date

class AdminService:
    def __init__(self, socio_repo, cobros_repo):
        self.socio_repo = socio_repo
        self.cobros_repo = cobros_repo

    def obtener_padron_completo(self):
        socios_crudos = self.socio_repo.obtener_todos()
        return [self._procesar_socio(s) for s in socios_crudos]

    def eliminar_socio(self, dni):
        try:
            self.socio_repo.eliminar(dni)
            return True
        except Exception as e:
            print(f"Error borrando socio: {e}")
            raise e

    def buscar_socio_para_cobrar(self, dni):
        # 1. Buscamos socio
        socio = self.socio_repo.obtener_por_dni(dni)
        if not socio:
            return None 

        # 2. Buscamos vencimiento
        vencimiento = self.cobros_repo.obtener_vencimiento(dni)
        
        # 3. Unificamos datos antes de procesar
        socio['vencimiento'] = vencimiento 
        
        # Devuelve un objeto PLANO (ej: {'nombre': 'Juan', 'estado': 'AL_DIA'})
        return self._procesar_socio(socio)

    def _procesar_socio(self, socio):
        # 1. Buscamos el último pago registrado
        ultimo_pago = self.cobros_repo.obtener_ultimo_pago(socio['dni'])
        
        estado_codigo = "SIN_CUOTA" 
        texto_vencimiento = "-"
        actividad_actual = "---" # Valor por defecto si no hay pagos

        if ultimo_pago:
            # --- A. CÁLCULO DE FECHAS (Tu lógica existente) ---
            vencimiento_str = ultimo_pago['fecha_vencimiento']
            try:
                fecha_vence = datetime.strptime(vencimiento_str, "%Y-%m-%d").date()
                hoy = date.today()
                
                texto_vencimiento = fecha_vence.strftime("%d/%m/%Y")
                
                if (fecha_vence - hoy).days >= 0:
                    estado_codigo = "AL_DIA"
                else:
                    dias_vencido = (hoy - fecha_vence).days
                    if dias_vencido > 60:  # Más de 2 meses (aprox.)
                        estado_codigo = "INACTIVO"
                    else:
                        estado_codigo = "VENCIDO"
            except:
                pass

            # --- B. EXTRACCIÓN DE ACTIVIDAD (NUEVO) ---
            # El concepto guardado es "Renovación: Body Pump"
            concepto = ultimo_pago.get('concepto', '')
            
            # Limpiamos el texto para que quede solo la actividad
            actividad_actual = concepto.replace("Renovación: ", "").replace("Renovación - ", "").replace("Inscripción - ", "")

        # 2. Inyectamos los datos calculados en el socio
        socio['estado'] = estado_codigo
        socio['vencimiento_str'] = texto_vencimiento
        socio['actividad'] = actividad_actual 
        
        return socio