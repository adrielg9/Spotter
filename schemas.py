from pydantic import BaseModel, field_validator
import re

# 1. Lógica compartida
def _validar_dni_logica(v: str) -> str:
    v = v.strip().replace(".", "")
    if not v.isdigit() or len(v) != 8:
        raise ValueError('El DNI debe ser numérico y de 8 dígitos exactos.')
    return v

def _validar_monto_logica(v: float) -> float:
    if v <= 0:
        raise ValueError('El monto debe ser mayor a $0.')
    return v

# 2. Check-In
class CheckInInput(BaseModel):
    dni: str
    @field_validator('dni')
    def validar_dni(cls, v): return _validar_dni_logica(v)

# 3. Alta de Socio (Registro Completo)
class UsuarioInput(BaseModel):
    dni: str
    nombre: str
    telefono: str


    @field_validator('dni')
    def validar_dni(cls, v): return _validar_dni_logica(v)

    @field_validator('nombre')
    def validar_nombre(cls, v):
        if len(v.strip()) < 3: raise ValueError('Nombre muy corto.')
        return v.strip().title()

    @field_validator('telefono')
    def validar_telefono(cls, v):
        limpio = v.strip().replace("-", "").replace(" ", "")
        if not re.match(r'^(?:11|[2368]\d{1,3})\d+$', limpio) or len(limpio) < 10:
             raise ValueError('Teléfono inválido. Sin 0 ni 15.')
        return limpio
    

# 4. Renovación (Caja)
class RenovacionInput(BaseModel):
    dni: str
    meses: int
    monto: float
    @field_validator('dni')
    def validar_dni(cls, v): return _validar_dni_logica(v)
    @field_validator('monto')
    def validar_monto(cls, v): return _validar_monto_logica(v)

# --- 5. NUEVO ESQUEMA DE EDICIÓN (SOLO NOMBRE Y TEL) ---
class EdicionSocioInput(BaseModel):
    dni: str
    nombre: str
    telefono: str

    @field_validator('dni')
    def validar_dni(cls, v): return _validar_dni_logica(v)

    @field_validator('nombre')
    def validar_nombre(cls, v):
        if len(v.strip()) < 3: raise ValueError('Nombre muy corto.')
        return v.strip().title()

    @field_validator('telefono')
    def validar_telefono(cls, v):
        limpio = v.strip().replace("-", "").replace(" ", "")
        if not re.match(r'^(?:11|[2368]\d{1,3})\d+$', limpio) or len(limpio) < 10:
             raise ValueError('Teléfono inválido. Solo Codigo de Área y Número.')
        return limpio