import os
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.importer_config import ImporterConfig

DB_USER = os.getenv('DB_USER', 'admin')
DB_PASS = os.getenv('DB_PASS', 'admin')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'importapp_db')

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

configs = session.query(ImporterConfig).all()
if not configs:
    print("No hay configuraciones en la tabla importer_configs.")
else:
    print("Configuraciones encontradas en la base de datos:")
    for config in configs:
        print(f"importer_name: {config.importer_name}")
        print(f"display_name: {config.display_name}")
        print(f"is_active: {config.is_active}")
        print(f"config_fields: {config.config_fields}")
        print(f"created_at: {config.created_at}")
        print(f"updated_at: {config.updated_at}")
        print("-"*40)
