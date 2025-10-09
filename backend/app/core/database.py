
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Detectar si estamos corriendo dentro de Docker o en el host
def get_database_url():
    # Si existe la variable de entorno DATABASE_URL, usarla
    if "DATABASE_URL" in os.environ:
        return os.environ["DATABASE_URL"]
    
    # Fallback usando variables de entorno individuales
    db_user = os.environ.get("POSTGRES_USER", "syncar_admin")
    db_password = os.environ.get("POSTGRES_PASSWORD", "syncar123456")
    db_name = os.environ.get("POSTGRES_DB", "syncar_db")
    
    # Si estamos en Docker, usar 'postgres' como hostname
    if os.path.exists("/.dockerenv"):
        return f"postgresql://{db_user}:{db_password}@postgres:5432/{db_name}"
    
    # Si estamos en el host (desarrollo), usar 'localhost'
    return f"postgresql://{db_user}:{db_password}@localhost:5432/{db_name}"

DATABASE_URL = get_database_url()

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
