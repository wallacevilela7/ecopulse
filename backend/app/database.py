"""
Módulo de conexão com o banco de dados via SQLAlchemy (EcoPulse).
Suporta SQLite (desenvolvimento local) e PostgreSQL (AWS RDS em produção).
"""
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ecopulse.db")


def criar_engine(url: str):
    connect_args = {}
    if url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    
    try:
        eng = create_engine(
            url,
            connect_args=connect_args,
            pool_pre_ping=True,
        )
        # Testa se a conexão é viável (para PostgreSQL remoto/local)
        if not url.startswith("sqlite"):
            with eng.connect():
                pass
        return eng
    except Exception:
        print("[DATABASE] PostgreSQL inacessível no momento. Ativando fallback para SQLite local.", file=sys.stderr)
        return create_engine("sqlite:///./ecopulse.db", connect_args={"check_same_thread": False})


engine = criar_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Injeção de dependência para sessões do banco de dados no FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
