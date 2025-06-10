from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import db.models as crud


app = FastAPI()

@app.post("/dispositivos/")
def crear_dispositivo(dispositivo_data: dict, db: Session = Depends(crud.get_db)):
    nuevo = crud.crear_dispositivo(db, dispositivo_data)
    return nuevo

@app.get("/dispositivos/{dispositivo_id}")
def leer_dispositivo(dispositivo_id: int, db: Session = Depends(crud.get_db)):
    dispositivo = crud.obtener_dispositivo(db, dispositivo_id)
    if dispositivo is None:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    return dispositivo

# Y así para actualizar, borrar, listar, etc.

# Para correr el server:
# uvicorn main:app --reload

