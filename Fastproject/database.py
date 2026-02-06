from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

USER = "postgres"
PASSWORD = "17477321"  # Твій цифровий пароль
HOST = "localhost"
PORT = "5432"
DB_NAME = "contacts_db"

# Використовуємо новий драйвер psycopg (версія 3)
SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # Цей драйвер зазвичай автоматично вирішує проблеми з UTF-8
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()