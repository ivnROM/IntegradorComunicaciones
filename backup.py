import telnetlib
import paramiko
from datetime import datetime
import os

def generar_backup_manual(dispositivo):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # VER SSH
    try:
        # Conexión Telnet
        print(dispositivo["ip"])
        print(dispositivo["usuario"])
        print(dispositivo["contrasena"])
        ssh.connect(hostname=dispositivo["ip"], username=dispositivo["usuario"], password=dispositivo["contrasena"], look_for_keys=False, allow_agent=False, timeout=10)
        print("Se pudo ingresar")
        stdin, stdout, stderr = ssh.exec_command("export")
        contents =stdout.read().decode()


        # Path de guardado
        path = dispositivo.get("b_path") or os.getcwd()
        os.makedirs(path, exist_ok=True)

        # Nombre del archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"{dispositivo['nombre']}_backup_{timestamp}.rsc"
        ruta_completa = os.path.join(path, nombre_archivo)

        with open(ruta_completa, "w") as f:
            f.write(contents)

        print(f"Backup de {dispositivo['nombre']} guardado en {ruta_completa}")

    except Exception as e:
        print(f"Error en backup de {dispositivo['nombre']}: {e}")
    finally:
        ssh.close()

