from typing import Optional
from fastapi import FastAPI, HTTPException
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

DATABASE_URL = "sqlite:///./users.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    plataforma = Column(String, index=True)
    correo = Column(String, index=True)
    password = Column(String)


class UsuarioPydantic(BaseModel):
    id : int
    plataforma: str
    correo: str
    password: str


class UsuarioCreate(BaseModel):
    plataforma: str
    correo: str
    password: str


class UsuarioUpdate(BaseModel):
    plataforma: Optional[str] = None
    correo: Optional[str] = None
    password: Optional[str] = None

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir solicitudes desde cualquier origen
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Permitir estos métodos HTTP
    allow_headers=["*"]  # Permitir todos los encabezados en las solicitudes
)


@app.post("/usuarios/", response_model=UsuarioCreate)
async def crear_usuario(usuario: UsuarioCreate):
    db = SessionLocal()
    db_usuario = Usuario(**usuario.dict())
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return {
        'id': db_usuario.id,
        'plataforma': db_usuario.plataforma,
        'correo': db_usuario.correo,
        'password': db_usuario.password
    }

@app.get("/usuarios/", response_model=list[UsuarioPydantic])
async def obtener_usuarios():
    db = SessionLocal()
    usuarios = db.query(Usuario).all()
    return [
        {
            'id': usuario.id,
            'plataforma': usuario.plataforma,
            'correo': usuario.correo,
            'password': usuario.password
        }
        for usuario in usuarios
    ]


@app.get("/usuarios/{usuario_id}", response_model=UsuarioPydantic)
async def obtener_usuario(usuario_id: int):
    db = SessionLocal()
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {
        'id': usuario.id,
        'plataforma': usuario.plataforma,
        'correo': usuario.correo,
        'password': usuario.password
    }


@app.put("/usuarios/{usuario_id}", response_model=UsuarioUpdate)
async def actualizar_usuario(usuario_id: int, usuario: UsuarioUpdate):
    db = SessionLocal()
    db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    for var, value in vars(usuario).items():
        if value is not None:
            setattr(db_usuario, var, value)
    db.commit()
    db.refresh(db_usuario)
    return {
        'id': db_usuario.id,
        'actualizado': True,
        'plataforma': db_usuario.plataforma,
        'correo': db_usuario.correo,
        'password': db_usuario.password
    }


@app.delete("/usuarios/{usuario_id}")
async def eliminar_usuario(usuario_id: int):
    db = SessionLocal()
    db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(db_usuario)
    db.commit()
    return {"id": usuario_id, "message": "Usuario eliminado correctamente"}


