from sqlalchemy.orm import Session
from models import get_db
from crud import *

# ⬇️ Simulación de campos de un widget o config
nombre = "Router Principal"
ip = "192.168.0.1"
tipo = "mikrotik"
usuario = "admin"
contrasena = "1234"
puerto = 22
b_periodo = "diario"
b_hora = "03:00"
b_dia = None
b_mes = None
b_path = "/backups/router"

# ⬇️ Crear un objeto tipo DispositivoCreate
nuevo_dispositivo = DispositivoCreate(
    nombre=nombre,
    ip=ip,
    tipo=tipo,
    usuario=usuario,
    contrasena=contrasena,
    puerto=puerto,
    b_periodo=b_periodo,
    b_hora=b_hora,
    b_dia=b_dia,
    b_mes=b_mes,
    b_path=b_path,
)

# ⬇️ Interactuar con la DB usando un contexto
def main():
    db_gen = get_db()
    db: Session = next(db_gen)

    # Crear
    creado = crear_dispositivo(db, nuevo_dispositivo)
    print("Dispositivo creado con ID:", creado.id)

    # Leer
    dispositivo = obtener_dispositivo(db, creado.id)
    print("Nombre del dispositivo:", dispositivo.nombre)

    # Listar
    todos = listar_dispositivos(db)
    print("Hay", len(todos), "dispositivos en total.")

    # Actualizar
    cambios = {"nombre": "Router Modificado", "puerto": 2222}
    actualizado = actualizar_dispositivo(db, creado.id, cambios)
    print("Nombre actualizado:", actualizado.nombre)

    # Borrar
    borrado = borrar_dispositivo(db, creado.id)
    print("Borrado:", "Sí" if borrado else "No")

    db_gen.close()

if __name__ == "__main__":
    main()

