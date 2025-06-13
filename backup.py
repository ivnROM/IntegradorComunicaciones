import telnetlib
import os

def generar_backup_manual(dispositivo):
    # VER SSH
    try:
        # Conexión Telnet
        tn = telnetlib.Telnet(dispositivo["ip"], int(dispositivo["puerto"]), timeout=5)
        
        # Login
        tn.read_until(b"Login: ")
        tn.write(dispositivo["usuario"].encode("ascii") + b"\n")
        
        tn.read_until(b"Password: ")
        tn.write(dispositivo["contrasena"].encode("ascii") + b"\n")
        
        # Comando export
        tn.write(b"export\n")
        time.sleep(2)  # Esperar que se genere la salida
        tn.write(b"exit\n")

        output = tn.read_all().decode("utf-8", errors="ignore")
        
        # Path de guardado
        path = dispositivo.get("b_path") or os.getcwd()
        os.makedirs(path, exist_ok=True)
        
        # Nombre del archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"{dispositivo['nombre']}_backup_{timestamp}.rsc"
        ruta_completa = os.path.join(path, nombre_archivo)
        
        with open(ruta_completa, "w") as f:
            f.write(output)
        
        print(f"Backup de {dispositivo['nombre']} guardado en {ruta_completa}")
    
    except Exception as e:
        print(f"Error en backup de {dispositivo['nombre']}: {e}")

