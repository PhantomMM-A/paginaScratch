import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, Date, Boolean
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

class Estudiante(Base):
    __tablename__ = "estudiantes"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    grado = Column(String(20), nullable=False)  # '5' or '6'

class RegistroAsistencia(Base):
    __tablename__ = "registros_asistencia"
    id = Column(Integer, primary_key=True, index=True)
    estudiante_id = Column(Integer, ForeignKey("estudiantes.id", ondelete="CASCADE"))
    fecha = Column(Date, nullable=False)
    tema = Column(String(200))
    estado = Column(String(30), default="Ausente")  # Presente / Ausente / Tardanza

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

# --- Schemas para Estudiantes y Asistencia ---
class EstudianteCreate(BaseModel):
    nombre: str
    grado: str

class EstudianteResponse(BaseModel):
    id: int
    nombre: str
    grado: str
    class Config:
        from_attributes = True

class AsistenciaCreate(BaseModel):
    estudiante_id: int
    fecha: date
    tema: Optional[str] = None
    estado: str = "Ausente"

class AsistenciaResponse(BaseModel):
    id: int
    estudiante_id: int
    fecha: date
    tema: Optional[str] = None
    estado: str
    class Config:
        from_attributes = True

class AsistenciaUpdate(BaseModel):
    estado: str

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

# --- Endpoints de Estudiantes ---
@app.get("/api/estudiantes", response_model=List[EstudianteResponse])
def listar_estudiantes(grado: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Estudiante)
    if grado:
        query = query.filter(Estudiante.grado == grado)
    return query.order_by(Estudiante.nombre).all()

@app.post("/api/estudiantes", response_model=EstudianteResponse, status_code=201)
def crear_estudiante(data: EstudianteCreate, db: Session = Depends(get_db)):
    estudiante = Estudiante(nombre=data.nombre.strip(), grado=data.grado)
    db.add(estudiante)
    db.commit()
    db.refresh(estudiante)
    return estudiante

@app.delete("/api/estudiantes/{id}", status_code=204)
def eliminar_estudiante(id: int, db: Session = Depends(get_db)):
    e = db.query(Estudiante).filter(Estudiante.id == id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    db.delete(e)
    db.commit()
    return

# --- Endpoints de Asistencia ---
@app.get("/api/asistencia", response_model=List[AsistenciaResponse])
def listar_asistencia(
    fecha: Optional[date] = None,
    grado: Optional[str] = None,
    estado: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(RegistroAsistencia)
    if fecha:
        query = query.filter(RegistroAsistencia.fecha == fecha)
    if estado:
        query = query.filter(RegistroAsistencia.estado == estado)
    if grado:
        # Join con Estudiante para filtrar por grado
        query = query.join(Estudiante, RegistroAsistencia.estudiante_id == Estudiante.id)
        query = query.filter(Estudiante.grado == grado)
    return query.all()

@app.post("/api/asistencia", response_model=AsistenciaResponse, status_code=201)
def crear_registro_asistencia(data: AsistenciaCreate, db: Session = Depends(get_db)):
    # Buscar si ya existe un registro para ese estudiante en esa fecha
    registro = db.query(RegistroAsistencia).filter(
        RegistroAsistencia.estudiante_id == data.estudiante_id,
        RegistroAsistencia.fecha == data.fecha
    ).first()
    
    if registro:
        # Si ya existe, actualizamos el estado y el tema
        registro.estado = data.estado
        if data.tema:
            registro.tema = data.tema
    else:
        # Si no existe, creamos uno nuevo
        registro = RegistroAsistencia(
            estudiante_id=data.estudiante_id,
            fecha=data.fecha,
            tema=data.tema,
            estado=data.estado
        )
        db.add(registro)
        
    db.commit()
    db.refresh(registro)
    return registro

@app.patch("/api/asistencia/{id}", response_model=AsistenciaResponse)
def actualizar_estado_asistencia(id: int, data: AsistenciaUpdate, db: Session = Depends(get_db)):
    registro = db.query(RegistroAsistencia).filter(RegistroAsistencia.id == id).first()
    if not registro:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    registro.estado = data.estado
    db.commit()
    db.refresh(registro)
    return registro

@app.delete("/api/asistencia/{id}", status_code=204)
def eliminar_registro_asistencia(id: int, db: Session = Depends(get_db)):
    registro = db.query(RegistroAsistencia).filter(RegistroAsistencia.id == id).first()
    if not registro:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    db.delete(registro)
    db.commit()
    return

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