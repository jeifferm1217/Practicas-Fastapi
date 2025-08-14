from fastapi import FastAPI
from .routers import users

app = FastAPI(
    title="API de Gestión de Tareas Personales",
    description="Una API completa para gestionar tareas, usuarios, categorías y estadísticas.",
    version="1.0.0",
)

# Esto debe estar presente y sin errores
app.include_router(users.router, prefix="/users", tags=["users"])

@app.get("/")
def read_root():
    return {"message": "¡Bienvenido a la API de Gestión de Tareas Personales!"}