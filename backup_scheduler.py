"""
Módulo de Backups Automáticos
Este módulo se encarga de verificar y ejecutar backups automáticos según la configuración
de cada dispositivo (diario, semanal, mensual).
"""

import os
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backup_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BackupScheduler:
    def __init__(self, db_session_func=None, check_interval=60):
        """
        Inicializa el programador de backups
        
        Args:
            db_session_func: Función que retorna una sesión de base de datos
            check_interval (int): Intervalo en segundos para verificar backups (default: 60)
        """
        self.get_db = db_session_func
        self.check_interval = check_interval
        self.running = False
        self.thread = None
        
    def start(self):
        """Inicia el servicio de backups automáticos"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.thread.start()
            logger.info("Servicio de backups automáticos iniciado")
        else:
            logger.warning("El servicio ya está en ejecución")
    
    def stop(self):
        """Detiene el servicio de backups automáticos"""
        self.running = False
        if self.thread:
            self.thread.join()
        logger.info("Servicio de backups automáticos detenido")
    
    def _run_scheduler(self):
        """Bucle principal del programador"""
        logger.info(f"Iniciando verificaciones cada {self.check_interval} segundos")
        
        while self.running:
            try:
                self._check_and_execute_backups()
            except Exception as e:
                logger.error(f"Error en el ciclo de verificación: {e}")
            
            # Esperar antes de la próxima verificación
            time.sleep(self.check_interval)
    
    def _check_and_execute_backups(self):
        """Verifica todos los dispositivos y ejecuta backups si es necesario"""
        try:
            # Obtener lista de dispositivos desde la API
            dispositivos = self._get_dispositivos()
            
            if not dispositivos:
                logger.debug("No hay dispositivos configurados")
                return
            
            logger.debug(f"Verificando {len(dispositivos)} dispositivos")
            
            for dispositivo in dispositivos:
                try:
                    if self._should_backup(dispositivo):
                        logger.info(f"Iniciando backup para {dispositivo['nombre']} ({dispositivo['ip']})")
                        self._execute_backup(dispositivo)
                    else:
                        logger.debug(f"No es hora de backup para {dispositivo['nombre']}")
                        
                except Exception as e:
                    logger.error(f"Error verificando dispositivo {dispositivo.get('nombre', 'desconocido')}: {e}")
                    
        except Exception as e:
            logger.error(f"Error obteniendo dispositivos: {e}")
    
    def _get_dispositivos(self):
        """Obtiene la lista de dispositivos desde la base de datos"""
        try:
            if not self.get_db:
                logger.error("No se configuró la función de base de datos")
                return []
            
            db = self.get_db()
            try:
                # Importar aquí para evitar dependencias circulares
                from crud import listar_dispositivos
                dispositivos = listar_dispositivos(db)
                
                # Convertir a diccionarios para facilitar el manejo
                dispositivos_dict = []
                for disp in dispositivos:
                    dispositivos_dict.append({
                        'id': disp.id,
                        'nombre': disp.nombre,
                        'ip': disp.ip,
                        'tipo': disp.tipo,
                        'usuario': disp.usuario,
                        'contrasena': disp.contrasena,
                        'puerto': disp.puerto,
                        'b_periodo': disp.b_periodo,
                        'b_hora': disp.b_hora,
                        'b_dia': disp.b_dia,
                        'b_path': disp.b_path
                    })
                
                return dispositivos_dict
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error obteniendo dispositivos desde la BD: {e}")
            return []
    
    def _should_backup(self, dispositivo):
        """
        Determina si un dispositivo necesita backup basado en su configuración
        
        Args:
            dispositivo (dict): Datos del dispositivo
            
        Returns:
            bool: True si necesita backup, False si no
        """
        # Verificar si tiene configuración de backup
        b_periodo = dispositivo.get('b_periodo')
        b_path = dispositivo.get('b_path')
        
        if not b_periodo or not b_path:
            logger.debug(f"Dispositivo {dispositivo['nombre']} sin configuración de backup completa")
            return False
        
        # Verificar si el directorio existe
        if not os.path.exists(b_path):
            logger.warning(f"El directorio de backup {b_path} no existe para {dispositivo['nombre']}")
            return False
        
        # Obtener la fecha del último backup
        ultimo_backup = self._get_last_backup_time(dispositivo)
        ahora = datetime.now()
        
        # Determinar si es hora de hacer backup según el período
        if b_periodo == "diario":
            return self._should_backup_daily(dispositivo, ultimo_backup, ahora)
        elif b_periodo == "semanal":
            return self._should_backup_weekly(dispositivo, ultimo_backup, ahora)
        elif b_periodo == "mensual":
            return self._should_backup_monthly(dispositivo, ultimo_backup, ahora)
        else:
            logger.warning(f"Período de backup desconocido: {b_periodo}")
            return False
    
    def _get_last_backup_time(self, dispositivo):
        """
        Obtiene la fecha de creación del último backup
        
        Args:
            dispositivo (dict): Datos del dispositivo
            
        Returns:
            datetime: Fecha del último backup o None si no existe
        """
        try:
            b_path = dispositivo['b_path']
            nombre = dispositivo['nombre']
            
            # Buscar archivos de backup para este dispositivo
            backup_files = []
            for file in os.listdir(b_path):
                if file.startswith(f"backup_{nombre}_") and (file.endswith('.txt') or file.endswith('.cfg')):
                    file_path = os.path.join(b_path, file)
                    # Usar fecha de creación del archivo
                    creation_time = os.path.getctime(file_path)
                    backup_files.append((file_path, creation_time))
            
            if backup_files:
                # Obtener el archivo más reciente
                ultimo_archivo = max(backup_files, key=lambda x: x[1])
                return datetime.fromtimestamp(ultimo_archivo[1])
            else:
                logger.debug(f"No se encontraron backups previos para {nombre}")
                return None
                
        except Exception as e:
            logger.error(f"Error obteniendo fecha del último backup para {dispositivo['nombre']}: {e}")
            return None
    
    def _should_backup_daily(self, dispositivo, ultimo_backup, ahora):
        """Verifica si debe hacer backup diario"""
        b_hora = dispositivo.get('b_hora')
        
        if not ultimo_backup:
            # Si no hay backup previo, verificar si es la hora correcta
            if b_hora:
                hora, minuto = map(int, b_hora.split(':'))
                hora_backup = ahora.replace(hour=hora, minute=minuto, second=0, microsecond=0)
                # Si ya pasó la hora de hoy, hacer backup
                return ahora >= hora_backup
            else:
                # Si no hay hora específica, hacer backup inmediatamente
                return True
        
        # Si hay backup previo, verificar si pasó un día completo
        if b_hora:
            # Con hora específica
            hora, minuto = map(int, b_hora.split(':'))
            hora_backup_hoy = ahora.replace(hour=hora, minute=minuto, second=0, microsecond=0)
            
            # Si ya pasó la hora de hoy y el último backup fue antes de hoy
            return (ahora >= hora_backup_hoy and 
                    ultimo_backup.date() < ahora.date())
        else:
            # Sin hora específica, verificar si pasó 24 horas
            return (ahora - ultimo_backup) >= timedelta(days=1)
    
    def _should_backup_weekly(self, dispositivo, ultimo_backup, ahora):
        """Verifica si debe hacer backup semanal"""
        b_dia = dispositivo.get('b_dia')  # 1=Lunes, 7=Domingo
        b_hora = dispositivo.get('b_hora')
        
        if not b_dia:
            logger.warning(f"Dispositivo {dispositivo['nombre']} con período semanal pero sin día configurado")
            return False
        
        # Convertir día de la semana (1=Lunes en nuestra config, pero Python usa 0=Lunes)
        dia_semana_config = int(b_dia) - 1  # Convertir a formato Python
        
        if not ultimo_backup:
            # Si no hay backup previo, verificar si es el día y hora correctos
            if ahora.weekday() == dia_semana_config:
                if b_hora:
                    hora, minuto = map(int, b_hora.split(':'))
                    hora_backup = ahora.replace(hour=hora, minute=minuto, second=0, microsecond=0)
                    return ahora >= hora_backup
                else:
                    return True
            return False
        
        # Si hay backup previo, verificar si pasó una semana y es el día correcto
        if ahora.weekday() == dia_semana_config:
            dias_desde_ultimo = (ahora.date() - ultimo_backup.date()).days
            
            if dias_desde_ultimo >= 7:  # Al menos una semana
                if b_hora:
                    hora, minuto = map(int, b_hora.split(':'))
                    hora_backup = ahora.replace(hour=hora, minute=minuto, second=0, microsecond=0)
                    return ahora >= hora_backup
                else:
                    return True
        
        return False
    
    def _should_backup_monthly(self, dispositivo, ultimo_backup, ahora):
        """Verifica si debe hacer backup mensual"""
        b_dia = dispositivo.get('b_dia')  # Día del mes (1-28)
        b_hora = dispositivo.get('b_hora')
        
        if not b_dia:
            logger.warning(f"Dispositivo {dispositivo['nombre']} con período mensual pero sin día configurado")
            return False
        
        dia_mes = int(b_dia)
        
        if not ultimo_backup:
            # Si no hay backup previo, verificar si es el día y hora correctos
            if ahora.day == dia_mes:
                if b_hora:
                    hora, minuto = map(int, b_hora.split(':'))
                    hora_backup = ahora.replace(hour=hora, minute=minuto, second=0, microsecond=0)
                    return ahora >= hora_backup
                else:
                    return True
            return False
        
        # Si hay backup previo, verificar si pasó un mes y es el día correcto
        if ahora.day == dia_mes:
            # Verificar si el último backup fue en un mes anterior
            if (ahora.year > ultimo_backup.year or 
                (ahora.year == ultimo_backup.year and ahora.month > ultimo_backup.month)):
                
                if b_hora:
                    hora, minuto = map(int, b_hora.split(':'))
                    hora_backup = ahora.replace(hour=hora, minute=minuto, second=0, microsecond=0)
                    return ahora >= hora_backup
                else:
                    return True
        
        return False
    
    def _execute_backup(self, dispositivo):
        """
        Ejecuta el backup para un dispositivo específico
        
        Args:
            dispositivo (dict): Datos del dispositivo
        """
        try:
            logger.info(f"Ejecutando backup para {dispositivo['nombre']} - {dispositivo['ip']}")
            
            # ACA PONE EL LLAMADO A GENERAR EL BACKUP DEL DISPOSITIVO
            # Ejemplo de llamada:
            # from backup import generar_backup_manual
            # generar_backup_manual(dispositivo)
            
            # Por ahora, simulamos el backup creando un archivo
            self._simulate_backup(dispositivo)
            
            logger.info(f"Backup completado para {dispositivo['nombre']}")
            
        except Exception as e:
            logger.error(f"Error ejecutando backup para {dispositivo['nombre']}: {e}")
    
    def _simulate_backup(self, dispositivo):
        """
        Simula un backup creando un archivo de prueba
        (Esta función se reemplazará por la llamada real al generador de backups)
        """
        try:
            b_path = dispositivo['b_path']
            nombre = dispositivo['nombre']
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            filename = f"backup_{nombre}_{timestamp}.txt"
            filepath = os.path.join(b_path, filename)
            
            with open(filepath, 'w') as f:
                f.write(f"Backup simulado para {nombre}\n")
                f.write(f"IP: {dispositivo['ip']}\n")
                f.write(f"Tipo: {dispositivo['tipo']}\n")
                f.write(f"Fecha: {datetime.now().isoformat()}\n")
            
            logger.info(f"Archivo de backup creado: {filepath}")
            
        except Exception as e:
            logger.error(f"Error creando archivo de backup simulado: {e}")


# Función para iniciar el servicio como daemon
def start_backup_service(db_session_func, check_interval=60):
    """
    Inicia el servicio de backups automáticos
    
    Args:
        db_session_func: Función que retorna una sesión de base de datos
        check_interval (int): Intervalo de verificación en segundos
    """
    scheduler = BackupScheduler(db_session_func, check_interval)
    scheduler.start()
    return scheduler


# Ejemplo de uso
if __name__ == "__main__":
    # Para uso independiente, necesitarías importar tu función get_db
    # from models import get_db
    # scheduler = start_backup_service(get_db)
    
    print("Para usar este módulo, impórtalo en tu API de FastAPI")
    print("Ejemplo:")
    print("from backup_scheduler import start_backup_service")
    print("from models import get_db")
    print("scheduler = start_backup_service(get_db)")
