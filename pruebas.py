import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from models import Base, DispositivoCreate, Dispositivo
from crud import crear_dispositivo, obtener_dispositivo, listar_dispositivos, actualizar_dispositivo, borrar_dispositivo

# Setup DB en memoria para tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    # Crear esquema
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)  # Limpia todo para la próxima prueba

# Datos comunes para crear dispositivos
dispositivo_data = DispositivoCreate(
    nombre="Router Principal",
    ip="192.168.0.1",
    tipo="mikrotik",
    usuario="admin",
    contrasena="1234",
    puerto=22,
    b_periodo="diario",
    b_hora="03:00",
    b_dia=None,
    b_mes=None,
    b_path="/backups/router",
)

def test_crear_y_leer_dispositivo(db):
    creado = crear_dispositivo(db, dispositivo_data)
    assert creado.id is not None
    assert creado.nombre == "Router Principal"

    encontrado = obtener_dispositivo(db, creado.id)
    assert encontrado is not None
    assert encontrado.ip == "192.168.0.1"

def test_listar_dispositivos(db):
    crear_dispositivo(db, dispositivo_data)
    crear_dispositivo(db, dispositivo_data.copy(update={"nombre": "Otro dispositivo", "ip": "10.0.0.2"}))
    
    dispositivos = listar_dispositivos(db)
    assert len(dispositivos) == 2

def test_actualizar_dispositivo(db):
    creado = crear_dispositivo(db, dispositivo_data)
    cambios = {"nombre": "Router Modificado", "puerto": 2222}
    actualizado = actualizar_dispositivo(db, creado.id, cambios)
    
    assert actualizado is not None
    assert actualizado.nombre == "Router Modificado"
    assert actualizado.puerto == 2222

def test_borrar_dispositivo(db):
    creado = crear_dispositivo(db, dispositivo_data)
    borrado = borrar_dispositivo(db, creado.id)
    assert borrado is True

    # Confirmar que ya no está
    dispositivo = obtener_dispositivo(db, creado.id)
    assert dispositivo is None

