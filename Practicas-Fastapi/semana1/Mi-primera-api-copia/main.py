from fastapi import FastAPI

# Crear la aplicación (lo más simple posible)
app = FastAPI(title="Mi Primera API")

# Endpoint 1: Hello World (OBLIGATORIO)
@app.get("/")
def hello_world():
    return {"message": "¡Mi primera API FastAPI!"}

# Endpoint 2: Info básica (OBLIGATORIO)
@app.get("/info")
def info():
    return {"api": "FastAPI", "week": 1, "status": "running"}
