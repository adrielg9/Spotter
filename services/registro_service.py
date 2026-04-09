from datetime import datetime, timedelta

class RegistroService:
    def __init__(self, socio_repo, cobros_repo):
        self.socio_repo = socio_repo
        self.cobros_repo = cobros_repo

    def buscar_por_dni(self, dni):
        return self.socio_repo.obtener_por_dni(dni)

    def registrar_socio(self, dni, nombre, telefono, monto, actividad="Cuota General", metodo_pago="Efectivo", usuario="Sistema"):
        # 1. Validamos si ya existe el socio
        if self.socio_repo.obtener_por_dni(dni):
            raise ValueError(f"El DNI {dni} ya está registrado.")

        # 2. Creamos el registro del socio
        exito_socio = self.socio_repo.crear(dni, nombre, telefono)
        if not exito_socio:
            raise Exception("No se pudo crear el socio en la base de datos.")

        # 3. Registramos el PAGO INICIAL automáticamente
        # Calculamos vencimiento a 30 días
        vencimiento = datetime.now() + timedelta(days=30)
        vencimiento_str = vencimiento.strftime('%Y-%m-%d')
        
        self.cobros_repo.registrar_transaccion(
            dni=dni,
            fecha_vencimiento=vencimiento_str,
            monto=monto,
            concepto=f"Alta - {actividad}",
            metodo_pago=metodo_pago,
            usuario=usuario
        )

        return True

    def actualizar_datos_socio(self, dni, nombre, telefono):
        if not self.socio_repo.obtener_por_dni(dni):
             raise ValueError(f"El socio con DNI {dni} no existe.")

        exito = self.socio_repo.actualizar(dni, nombre, telefono)
        
        if not exito:
            raise Exception("No se pudieron guardar los cambios en la base de datos.")
            
        return True