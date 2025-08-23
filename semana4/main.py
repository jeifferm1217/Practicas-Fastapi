from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import models
from database import engine, get_db
from sqlalchemy import text

# Crear las tablas en la base de datos
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FastAPI con SQLAlchemy",
    description="Setup básico de base de datos",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "FastAPI con SQLAlchemy funcionando!"}

@app.get("/test-db")
def test_database(db: Session = Depends(get_db)):
    """Endpoint para probar la conexión a la base de datos"""
    try:
        # Realizar una consulta simple
        result = db.execute(text("SELECT 1")).fetchone()
        return {"database": "connected", "test_query": result[0]}
    except Exception as e:
        return {"database": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
