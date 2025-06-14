from sqlalchemy.orm import Session
from models import Dispositivo, DispositivoCreate  

# Crear un dispositivo nuevo
def crear_dispositivo(db: Session, dispositivo_data: DispositivoCreate) -> Dispositivo:
    nuevo = Dispositivo(**dispositivo_data.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

# Obtener dispositivo por ID
def obtener_dispositivo(db: Session, dispositivo_id: int) -> Dispositivo | None:
    return db.query(Dispositivo).filter(Dispositivo.id == dispositivo_id).first()

# Listar todos los dispositivos
def listar_dispositivos(db: Session) -> list[Dispositivo]:
    return db.query(Dispositivo).all()

# Actualizar dispositivo (por ID)
def actualizar_dispositivo(db: Session, dispositivo_id: int, cambios: dict) -> Dispositivo | None:
    dispositivo = db.query(Dispositivo).filter(Dispositivo.id == dispositivo_id).first()
    if not dispositivo:
        return None
    for clave, valor in cambios.items():
        if hasattr(dispositivo, clave):
            setattr(dispositivo, clave, valor)
    db.commit()
    db.refresh(dispositivo)
    return dispositivo

# Borrar dispositivo (por ID)
def borrar_dispositivo(db: Session, dispositivo_id: int) -> bool:
    dispositivo = db.query(Dispositivo).filter(Dispositivo.id == dispositivo_id).first()
    if not dispositivo:
        return False
    db.delete(dispositivo)
    db.commit()
    return True
