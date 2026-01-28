from fastapi import FastAPI, Depends
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship

#Pfad zur DB
SQLALCHEMY_DATABASE_URL = "postgresql://user:password123@localhost:5432/UNSERtaube"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Tabellen in der DB erstellen (falls nicht vorhanden)
Base.metadata.create_all(bind=engine)

app = FastAPI()

# 3. Dependency: Holt eine DB-Sitzung für jeden Request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()