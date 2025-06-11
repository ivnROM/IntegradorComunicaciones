import json, threading, time
from datetime import datetime

TIEMPO_PATH = "tiempo.json"
INTERVALO_MINUTOS = 15

def cargar_tiempo():
    try:
        with open(TIEMPO_PATH, "r") as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        return {"ultima_actualizacion": datetime.utcnow().isoformat(), "minutos_acumulados": 0}

def guardar_tiempo(data):
    with open(TIEMPO_PATH, "w") as f:
        json.dump(data, f)

def actualizar_tiempo():
    while True:
        time.sleep(INTERVALO_MINUTOS * 60)
        data = cargar_tiempo()
        data["minutos_acumulados"] += INTERVALO_MINUTOS
        data["ultima_actualizacion"] = datetime.utcnow().isoformat()
        guardar_tiempo(data)

def iniciar_contador():
    hilo = threading.Thread(target=actualizar_tiempo, daemon=True)
    hilo.start()

