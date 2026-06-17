import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, Date
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from typing import List, Optional
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
    descripcion: Optional[str] = None
    pdf_url: Optional[str] = None
    imagen_url: Optional[str] = None
    autor: Optional[str] = None
    fecha: Optional[date] = None
    dificultad: Optional[str] = "Principiante"

    class Config:
        from_attributes = True

class GaleriaResponse(BaseModel):
    id: int
    grado_id: int
    imagen_url: str
    descripcion: Optional[str] = None
    fecha: Optional[date] = None

    class Config:
        from_attributes = True

class PlanificacionResponse(BaseModel):
    id: int
    grado_id: int
    titulo: str
    pdf_url: str
    numero_clase: Optional[int] = None
    fecha: Optional[date] = None

    class Config:
        from_attributes = True

# 4. Inicializar FastAPI
app = FastAPI(title="Codifica tu Mundo API", docs_url="/api/docs", openapi_url="/api/openapi.json")

# Crear tablas automáticamente si la conexión a la base de datos es exitosa
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Advertencia: No se pudieron crear las tablas de base de datos automáticamente: {e}")

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

@app.get("/api/proyectos", response_model=List[ProyectoResponse])
def listar_proyectos(grado_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Proyecto)
    if grado_id: 
        query = query.filter(Proyecto.grado_id == grado_id)
    return query.all()

@app.get("/api/galeria", response_model=List[GaleriaResponse])
def listar_galeria(grado_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Galeria)
    if grado_id: 
        query = query.filter(Galeria.grado_id == grado_id)
    return query.all()

@app.get("/api/planificaciones", response_model=List[PlanificacionResponse])
def listar_planificaciones(grado_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Planificacion)
    if grado_id: 
        query = query.filter(Planificacion.grado_id == grado_id)
    return query.all()

# 6. Servir Frontend Estático (HTML, CSS, JS)
@app.get("/")
def read_index():
    return FileResponse("index.html")

@app.get("/{filename}.html")
def read_html(filename: str):
    filepath = f"{filename}.html"
    if os.path.exists(filepath):
        return FileResponse(filepath)
    raise HTTPException(status_code=404, detail="Página no encontrada")

@app.get("/css/{filename}")
def read_css(filename: str):
    filepath = os.path.join("css", filename)
    if os.path.exists(filepath):
        return FileResponse(filepath)
    raise HTTPException(status_code=404, detail="Archivo CSS no encontrado")

@app.get("/js/{filename}")
def read_js(filename: str):
    filepath = os.path.join("js", filename)
    if os.path.exists(filepath):
        return FileResponse(filepath)
    raise HTTPException(status_code=404, detail="Archivo JS no encontrado")