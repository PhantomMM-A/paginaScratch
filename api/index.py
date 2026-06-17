import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, Date
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import date

# 1. Configuración de la Base de Datos
# Lee la variable de entorno de Vercel en producción, si no usa una local por defecto
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://usuario:password@localhost/dbname")

# Corrección para compatibilidad de esquemas de conexión en Vercel/Render/Supabase
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. Dependencia de conexión
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 3. Modelos de Base de Datos (SQLAlchemy)
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

# 4. Esquemas de validación (Pydantic)
class ProyectoResponse(BaseModel):
    id: int
    grado_id: int
    titulo: str
    descripcion: str | None = None
    pdf_url: str | None = None
    imagen_url: str | None = None
    autor: str | None = None
    fecha: date | None = None
    dificultad: str | None = "Principiante"

    class Config:
        from_attributes = True

# 5. Inicializar FastAPI
app = FastAPI(title="Feria de Ciencias API", docs_url="/api/docs", openapi_url="/api/openapi.json")

# Crear tablas automáticamente en la base de datos si no existen
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

# 6. Endpoints
@app.get("/api/status")
def status():
    return {"status": "online", "proyecto": "Backend Feria Scratch"}

@app.get("/api/proyectos", response_model=list[ProyectoResponse])
def listar_proyectos(grado_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(Proyecto)
    if grado_id:
        query = query.filter(Proyecto.grado_id == grado_id)
    return query.all()

@app.get("/api/proyectos/{proyecto_id}", response_model=ProyectoResponse)
def obtener_proyecto(proyecto_id: int, db: Session = Depends(get_db)):
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return proyecto