from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from pydantic import BaseModel

SQLALCHEMY_DATABASE_URL = "sqlite:///./devices.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# SQLAlchemy
class Dispositivo(Base):
    __tablename__ = "dispositivos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    ip = Column(String, nullable=False)
    tipo = Column(String, nullable=False)
    usuario = Column(String, nullable=False)
    contrasena = Column(String, nullable=False)
    puerto = Column(Integer, nullable=False)
    
    b_periodo = Column(String, nullable=True)     # "diario", "semanal", "mensual"
    b_hora = Column(String, nullable=True)        # Ej: "08:00"
    b_dia = Column(Integer, nullable=True)        # 0=lunes ... 6=domingo
    b_mes = Column(Integer, nullable=True)        # Ej: 1 (enero)
    b_path = Column(String, nullable=False)        # Ruta donde guardar backup

Base.metadata.create_all(bind=engine)

# Pydantic de entrada
class DispositivoCreate(BaseModel):
    nombre: str
    ip: str
    tipo: str
    usuario: str
    contrasena: str
    puerto: int
    b_periodo: str
    b_hora: str | None
    b_dia: int | None
    b_mes: int | None
    b_path: str | None

class DispositivoUpdate(BaseModel):
    nombre: str | None
    ip: str | None
    tipo: str | None
    usuario: str | None
    contrasena: str | None
    puerto: int |  None
    b_periodo: str | None
    b_hora: str | None
    b_dia: int | None
    b_mes: int | None
    b_path: str | None

# Pydantic de salida
class DispositivoOut(DispositivoCreate):
    id: int

    class Config:
        from_attributes = True


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
