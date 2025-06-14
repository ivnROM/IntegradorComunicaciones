import pytest
import os
import tempfile
import time
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from models import Base, DispositivoCreate, Dispositivo
from crud import crear_dispositivo, obtener_dispositivo, listar_dispositivos, actualizar_dispositivo, borrar_dispositivo
from backup_scheduler import BackupScheduler

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

@pytest.fixture
def temp_backup_dir():
    """Esto crea un directorio temporal para backups"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def mock_db_session():
    """ Clon de función get_db para los tests del scheduler"""
    def get_db_mock():
        db = TestingSessionLocal()
        Base.metadata.create_all(bind=engine)
        return db
    return get_db_mock

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

# ========== TESTS CRUD ORIGINALES ==========
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

# ========== TESTS DEL BACKUP SCHEDULER ==========

def test_backup_scheduler_initialization(mock_db_session):
    """Test que el scheduler se inicializa correctamente"""
    scheduler = BackupScheduler(mock_db_session, check_interval=30)
    
    assert scheduler.get_db == mock_db_session
    assert scheduler.check_interval == 30
    assert scheduler.running is False
    assert scheduler.thread is None

def test_backup_scheduler_start_stop(mock_db_session):
    """Test que el scheduler puede iniciar y parar correctamente"""
    scheduler = BackupScheduler(mock_db_session, check_interval=1)
    
    # Iniciar
    scheduler.start()
    assert scheduler.running is True
    assert scheduler.thread is not None
    
    # Parar
    scheduler.stop()
    assert scheduler.running is False

def test_get_dispositivos_from_db(db, mock_db_session):
    """Test que el scheduler puede obtener dispositivos desde la BD"""
    # Crear algunos dispositivos de prueba
    dispositivo1 = crear_dispositivo(db, dispositivo_data)
    dispositivo2_data = dispositivo_data.copy(update={"nombre": "Switch Test", "ip": "192.168.1.2"})
    dispositivo2 = crear_dispositivo(db, dispositivo2_data)
    
    # Configurar el mock para usar nuestra sesión de prueba
    def get_db_test():
        return db
    
    scheduler = BackupScheduler(get_db_test)
    dispositivos = scheduler._get_dispositivos()
    
    assert len(dispositivos) == 2
    assert dispositivos[0]['nombre'] == "Router Principal"
    assert dispositivos[1]['nombre'] == "Switch Test"

def test_should_backup_daily_sin_backup_previo(temp_backup_dir):
    """Test backup diario cuando no hay backup previo"""
    dispositivo = {
        'nombre': 'RouterTest',
        'ip': '192.168.1.1',
        'b_periodo': 'diario',
        'b_hora': '14:00',
        'b_path': temp_backup_dir
    }
    
    scheduler = BackupScheduler(None)
    
    # Datetime para simular que es las 15:00 (después de la hora programada)
    with patch('backup_scheduler.datetime') as mock_datetime:
        mock_now = datetime(2024, 1, 15, 15, 30, 0)  # 15:30
        mock_datetime.now.return_value = mock_now
        mock_datetime.fromtimestamp = datetime.fromtimestamp  # Para que funcione la función real
        
        should_backup = scheduler._should_backup(dispositivo)
        assert should_backup is True

def test_should_backup_weekly(temp_backup_dir):
    """Test backup semanal en el día correcto"""
    dispositivo = {
        'nombre': 'RouterTest',
        'ip': '192.168.1.1',
        'b_periodo': 'semanal',
        'b_hora': '14:00',
        'b_dia': '1',  # Lunes
        'b_path': temp_backup_dir
    }
    
    scheduler = BackupScheduler(None)
    
    # Datetime para simular que es lunes a las 15:00
    with patch('backup_scheduler.datetime') as mock_datetime:

        mock_now = datetime(2024, 1, 15, 15, 0, 0)  # Un lunes
        mock_datetime.now.return_value = mock_now
        mock_datetime.fromtimestamp = datetime.fromtimestamp
        
        should_backup = scheduler._should_backup(dispositivo)
        assert should_backup is True

def test_should_backup_monthly(temp_backup_dir):
    """Test backup mensual en el día correcto"""
    dispositivo = {
        'nombre': 'RouterTest',
        'ip': '192.168.1.1',
        'b_periodo': 'mensual',
        'b_hora': '14:00',
        'b_dia': '15',  # Test mensual un dia 15
        'b_path': temp_backup_dir
    }
    
    scheduler = BackupScheduler(None)
    
    # Datetime para simular que es día 15 a las 15:00
    with patch('backup_scheduler.datetime') as mock_datetime:
        mock_now = datetime(2024, 1, 15, 15, 0, 0)  # Día 15
        mock_datetime.now.return_value = mock_now
        mock_datetime.fromtimestamp = datetime.fromtimestamp
        
        should_backup = scheduler._should_backup(dispositivo)
        assert should_backup is True

def test_should_not_backup_sin_configuracion():
    """Test que no hace backup si no hay configuración completa"""
    dispositivo_sin_config = {
        'nombre': 'RouterTest',
        'ip': '192.168.1.1',
        'b_periodo': None,  # Sin período
        'b_path': None      # Sin path
    }
    
    scheduler = BackupScheduler(None)
    should_backup = scheduler._should_backup(dispositivo_sin_config)
    assert should_backup is False

def test_should_not_backup_directorio_inexistente():
    """Test que no hace backup si el directorio no existe"""
    dispositivo = {
        'nombre': 'RouterTest',
        'ip': '192.168.1.1',
        'b_periodo': 'diario',
        'b_hora': '14:00',
        'b_path': '/directorio/que/no/existe'
    }
    
    scheduler = BackupScheduler(None)
    should_backup = scheduler._should_backup(dispositivo)
    assert should_backup is False

def test_execute_backup_simulation(temp_backup_dir):
    """Test la ejecución simulada de backup"""
    dispositivo = {
        'nombre': 'RouterTest',
        'ip': '192.168.1.1',
        'tipo': 'router',
        'b_path': temp_backup_dir
    }
    
    scheduler = BackupScheduler(None)
    
    # Ejecutar backup simulado
    scheduler._execute_backup(dispositivo)
    
    # Verificar que se creó el archivo
    archivos = os.listdir(temp_backup_dir)
    archivos_backup = [f for f in archivos if f.startswith('backup_RouterTest_')]
    
    assert len(archivos_backup) == 1
    
    # Verificar contenido del archivo
    with open(os.path.join(temp_backup_dir, archivos_backup[0]), 'r') as f:
        contenido = f.read()
        assert 'RouterTest' in contenido
        assert '192.168.1.1' in contenido

def test_check_and_execute_backups_integration(db, temp_backup_dir):
    """Test de integración completo del proceso de verificación y ejecución"""
    # Crear dispositivo en la BD con configuración de backup
    dispositivo_data_backup = dispositivo_data.copy(update={
        'nombre': 'RouterIntegration',
        'b_periodo': 'diario',
        'b_hora': datetime.now().strftime('%H:%M'),  # Hora actual para que se ejecute
        'b_path': temp_backup_dir
    })
    
    creado = crear_dispositivo(db, dispositivo_data_backup)
    
    def get_db_test():
        return db
    
    scheduler = BackupScheduler(get_db_test, check_interval=1)
    
    # Ejecutar una verificación
    scheduler._check_and_execute_backups()
    
    # Verificar que se creó el backup
    archivos = os.listdir(temp_backup_dir)
    archivos_backup = [f for f in archivos if f.startswith('backup_RouterIntegration_')]
    
    assert len(archivos_backup) == 1
