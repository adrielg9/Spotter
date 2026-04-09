from datetime import datetime, timedelta
import calendar 

class CheckInService:
    def __init__(self, socio_repo, cobros_repo, asistencia_repo):
        self.socio_repo = socio_repo
        self.cobros_repo = cobros_repo
        self.asistencia_repo = asistencia_repo

    def registrar_ingreso(self, dni):
        # 1. Buscamos si el socio existe
        socio = self.socio_repo.obtener_por_dni(dni)
        if not socio:
            raise ValueError(f"El DNI {dni} no está registrado.")

        # --- VALIDACIÓN: Ya vino hoy? ---
        cant_hoy = self.asistencia_repo.contar_hoy(dni)
        
        if cant_hoy >= 1:
            return {
                "estado": "YA_ASISTIO",
                "nombre": socio['nombre'],
                "dni": dni,
                "dias": 0,
                "mensaje": "Ya registró su asistencia hoy"
            }

        # 2. Buscamos su fecha de vencimiento y CONCEPTO (Cuota)
        vencimiento_str = self.cobros_repo.obtener_vencimiento(dni)
        
        # --- NUEVA LÓGICA: Obtener concepto de la tabla Cobros ---
        # Llamamos al nuevo método del repositorio (que definiremos abajo)
        concepto_db = self.cobros_repo.obtener_ultimo_concepto(dni)
        
        # Limpiamos el texto: de "Renovación: Musculación" a solo "Musculación"
        if concepto_db:
            tipo_cuota = concepto_db.replace("Renovación: ", "").strip()
        else:
            tipo_cuota = "Cuota General"
        
        dias_restantes = -999 
        estado = "VENCIDO"
        fecha_pago_readable = "N/A"

        if vencimiento_str:
            fecha_vence = datetime.strptime(vencimiento_str, "%Y-%m-%d")
            hoy = datetime.now()
            delta = fecha_vence - hoy
            dias_restantes = delta.days + 1
            fecha_pago_readable = fecha_vence.strftime("%d/%m/%Y")
            
            if dias_restantes >= 0:
                estado = "AL_DIA"

        # 3. Lógica de Acceso
        if estado == "AL_DIA":
            self.asistencia_repo.registrar(dni)
            
        # 4. Retornamos el paquete de datos COMPLETO para la vista
        return {
            "estado": estado,
            "nombre": socio['nombre'],
            "dni": dni,
            "dias": dias_restantes,
            "cuota": tipo_cuota,            # <--- Extraído de la columna 'concepto'
            "ultimo_pago": fecha_pago_readable,
            "membresia": "Mensual"          # Valor por defecto o sacado de socio
        }

    def renovar_cuota(self, dni, meses, monto, actividad="Cuota General", metodo_pago="Efectivo", usuario="Sistema"):
        if not self.socio_repo.obtener_por_dni(dni):
            raise ValueError(f"No se puede cobrar. El DNI {dni} no existe.")

        vencimiento_actual_str = self.cobros_repo.obtener_vencimiento(dni)
        nueva_fecha_dt = self._calcular_nueva_fecha(vencimiento_actual_str, meses)

        # Aquí es donde guardas el concepto que luego leeremos
        concepto = f"Renovación: {actividad}"

        self.cobros_repo.registrar_transaccion(
            dni,
            nueva_fecha_dt.strftime('%Y-%m-%d'),
            float(monto),
            concepto,
            metodo_pago,
            usuario  
        )
        
        return nueva_fecha_dt.strftime("%d/%m/%Y") 

    def _calcular_nueva_fecha(self, vencimiento_str, meses):
        hoy = datetime.now()
        fecha_base = hoy 

    # 1. Determinar desde qué fecha arrancamos
        if vencimiento_str:
            try:
                vence_dt = datetime.strptime(vencimiento_str, "%Y-%m-%d")
            # Si vence en el futuro, sumamos a esa fecha. Si ya venció, sumamos a hoy.
                fecha_base = max(hoy, vence_dt)
            except ValueError:
                pass # Si la fecha viene mal, usamos hoy

        meses_a_sumar = int(meses)
    
        # 2. Lógica para sumar meses exactos (Mismo día del mes siguiente)
        # Calculamos el mes y año destino
        mes_nuevo = fecha_base.month + meses_a_sumar
        anio_extra = (mes_nuevo - 1) // 12
    
        anio_final = fecha_base.year + anio_extra
        mes_final = (mes_nuevo - 1) % 12 + 1
    
    # 3. Ajuste de días (El caso "31 de Enero")
    # Si la fecha base es día 31 y caemos en Febrero (que tiene 28), 
    # calendar.monthrange nos dice cuántos días tiene ese mes destino.
        _, dias_en_mes_destino = calendar.monthrange(anio_final, mes_final)
    
    # Elegimos el día: el original, o el máximo del mes si nos pasamos
        dia_final = min(fecha_base.day, dias_en_mes_destino)
    
        return fecha_base.replace(year=anio_final, month=mes_final, day=dia_final)