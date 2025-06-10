from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./devices.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Dispositivo(Base):
    __tablename__ = "dispositivos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    ip = Column(String, nullable=False)
    tipo = Column(String, nullable=False)
    usuario = Column(String, nullable=False)
    contraseña = Column(String, nullable=False)
    puerto = Column(Integer, nullable=False)

    # Backup settings
    b_periodo = Column(Integer, nullable=True)   # 1 = diario, 2 = semanal, 3 = mensual
    b_hora = Column(String, nullable=True)       # Ej: "08:00"
    b_dia = Column(String, nullable=True)        # Ej: "lunes"
    b_mes = Column(Integer, nullable=True)       # Ej: 1 (enero)
    b_path = Column(String, nullable=True)       # Ruta donde guardar backup

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Crear un dispositivo nuevo
def crear_dispositivo(db: Session, dispositivo_data: dict) -> Dispositivo:
    nuevo = Dispositivo(**dispositivo_data)
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

