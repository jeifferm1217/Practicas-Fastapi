#!/usr/bin/env python3
"""
Mi Primera API FastAPI - Verificación de Setup
Desarrollador: [Tu nombre se llenará automáticamente]
"""

from fastapi import FastAPI

app = FastAPI(title="Mi Primera API")

@app.get("/")
def hello_world():
    return {"message": "¡Mi primera API FastAPI!"}

@app.get("/info")
def info():
    return {"api": "FastAPI", "week": 1, "status": "running"}

@app.get("/greeting/{name}")
def greet_user(name: str):
    return {"greeting": f"¡Hola {name}!"}

@app.get("/my-profile")
def my_profile():
    return {
        "name": "Jeiffer",           # Cambiar por tu nombre
        "bootcamp": "FastAPI",
        "week": 1,
        "date": "2025",
        "likes_fastapi": True              # ¿Te gustó FastAPI?
    }
EOF

if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando servidor de verificación...")
    print("📍 Acceder a: http://localhost:8000")
    print("📖 Documentación: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
