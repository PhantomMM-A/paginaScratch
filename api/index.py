import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, Date
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from datetime import date

# 1. Configuración de la Base de Datos
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://usuario:password@localhost/dbname")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 2. Modelos de Base de Datos (SQLAlchemy)
class Grado(Base):
    __tablename__ = "grados"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
    descripcion = Column(Text)
    año = Column(Integer, default=2026)

class Proyecto(Base):
    __tablename__ = "proyectos"
    id = Column(Integer, primary_key=True, index=True)
    grado_id = Column(Integer, ForeignKey("grados.id", ondelete="CASCADE"))
    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text)
    pdf_url = Column(String(500))
    imagen_url = Column(String(500))
    autor = Column(String(100))
    fecha = Column(Date)
    dificultad = Column(String(50), default="Principiante")

class Galeria(Base):
    __tablename__ = "galeria"
    id = Column(Integer, primary_key=True, index=True)
    grado_id = Column(Integer, ForeignKey("grados.id", ondelete="CASCADE"))
    imagen_url = Column(String(500), nullable=False)
    descripcion = Column(String(300))
    fecha = Column(Date)

class Planificacion(Base):
    __tablename__ = "planificaciones"
    id = Column(Integer, primary_key=True, index=True)
    grado_id = Column(Integer, ForeignKey("grados.id", ondelete="CASCADE"))
    titulo = Column(String(200), nullable=False)
    pdf_url = Column(String(500), nullable=False)
    numero_clase = Column(Integer)
    fecha = Column(Date)

# 3. Esquemas de Pydantic para las respuestas de la API
class ProyectoResponse(BaseModel):
    id: int
    grado_id: int
    titulo: str
    descripcion: str | None = None
    pdf_url: str | None = None
    imagen_url: str | None = None
    autor: str | None = None
    fecha: date | None = None

    class Config:
        from_attributes = True

# 4. Inicializar FastAPI
app = FastAPI(title="Codifica tu Mundo API", docs_url="/api/docs", openapi_url="/api/openapi.json")

# Habilitar CORS para que tu frontend se pueda conectar sin bloqueos de seguridad
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. Endpoints (Rutas para el Frontend)
@app.get("/api/status")
def status():
    return {"status": "online", "proyecto": "Codifica tu Mundo - CRECE"}

@app.get("/api/proyectos", response_model=list[ProyectoResponse])
def listar_proyectos(grado_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(Proyecto)
    if grado_id: query = query.filter(Proyecto.grado_id == grado_id)
    return query.all()

@app.get("/api/galeria", response_model=list[GaleriaResponse])
def listar_galeria(grado_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(Galeria)
    if grado_id: query = query.filter(Galeria.grado_id == grado_id)
    return query.all()

@app.get("/api/planificaciones", response_model=list[PlanificacionResponse])
def listar_planificaciones(grado_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(Planificacion)
    if grado_id: query = query.filter(Planificacion.grado_id == grado_id)
    return query.all()