# db/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 🚀 URL de conexión para MySQL
# Formato: "mysql+pymysql://usuario:contraseña@servidor/nombre_de_la_bd"
# Asegúrate de reemplazar 'usuario', 'contraseña', 'servidor' y 'nombre_de_la_bd' con tus credenciales.
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root@localhost/jardineria"

# Conexión al motor
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

# Sesión local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
Base = declarative_base()


# Dependencia para obtener la sesión en los endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()