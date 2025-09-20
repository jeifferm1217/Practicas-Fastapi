from database import Base, engine
from models import User, Proyecto  # Importa todos tus modelos aquí

print("Creando tablas de la base de datos...")
Base.metadata.create_all(bind=engine)
print("¡Tablas creadas exitosamente!")