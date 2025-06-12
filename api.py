from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from contador import iniciar_contador
from models import *
from crud import *

app = FastAPI()
iniciar_contador()

# C - Crear dispositivo
@app.post("/dispositivos/", response_model=DispositivoOut)
def crear_dispositivo_endpoint(dispositivo_data: DispositivoCreate, db: Session = Depends(get_db)):
    nuevo = crear_dispositivo(db, dispositivo_data)
    return nuevo

# R - Obtener un dispositivo por ID
@app.get("/dispositivos/{dispositivo_id}", response_model=DispositivoOut)
def leer_dispositivo_endpoint(dispositivo_id: int, db: Session = Depends(get_db)):
    dispositivo = obtener_dispositivo(db, dispositivo_id)
    if dispositivo is None:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    return dispositivo

# R - Listar todos los dispositivos
@app.get("/dispositivos/", response_model=list[DispositivoOut])
def leer_todos_dispositivos_endpoint(db: Session = Depends(get_db)):
    return listar_dispositivos(db)

# U - Actualizar un dispositivo 
@app.put("/dispositivos/{dispositivo_id}", response_model=DispositivoOut)
def actualizar_dispositivo_endpoint(dispositivo_id: int, datos: DispositivoUpdate, db: Session = Depends(get_db)):
    cambios = datos.dict(exclude_unset=True)
    dispositivo_actualizado = actualizar_dispositivo(db, dispositivo_id, cambios)
    if dispositivo_actualizado is None:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    return dispositivo_actualizado

# D - Borrar un dispositivo
@app.delete("/dispositivos/{dispositivo_id}")
def borrar_dispositivo_endpoint(dispositivo_id: int, db: Session = Depends(get_db)):
    eliminado = borrar_dispositivo(db, dispositivo_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    return {"detail": "Dispositivo borrado correctamente"}

