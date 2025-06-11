from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from contador import iniciar_contador
import db.models as crud


#from programa import Dispositivo

app = FastAPI()
iniciar_contador()

# C
@app.post("/dispositivos/")
def crear_dispositivo(dispositivo_data: dict, db: Session = Depends(crud.get_db)):
    nuevo = crud.crear_dispositivo(db, dispositivo_data)
    return nuevo

# R
@app.get("/dispositivos/{dispositivo_id}")
def leer_dispositivo(dispositivo_id: int, db: Session = Depends(crud.get_db)):
    dispositivo = crud.obtener_dispositivo(db, dispositivo_id)
    if dispositivo is None:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    return dispositivo

@app.get("/dispositivos/")
def leer_todos_dispositivos(db: Session = Depends(crud.get_db)):
    return db.query(crud.Dispositivo).all()

# U
# @app.put("/dispositivos/{dispositivo_id}")
# def actualizar_dispositivo_endpoint(dispositivo_id: int, datos: DispositivoUpdate, db: Session = Depends(crud.get_db)):
#     dispositivo_actualizado = crud.actualizar_dispositivo(db, dispositivo_id, datos.dict(exclude_unset=True))
#     if dispositivo_actualizado is None:
#         raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
#     return dispositivo_actualizado

# D
@app.delete("/dispositivos/{dispositivo_id}")
def borrar_dispositivo(dispositivo_id: int, db: Session = Depends(crud.get_db)):
    dispositivo = crud.borrar_dispositivo(db, dispositivo_id)
    if dispositivo is None:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    return {"detail": "Dispositivo borrado correctamente"}
 #Y así para actualizar, borrar, listar, etc.

# Para correr el server:
# uvicorn main:app --reload

