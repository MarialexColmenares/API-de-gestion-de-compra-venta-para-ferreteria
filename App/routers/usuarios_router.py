from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from services.usuarios_services import crear_usuario_service, obtener_usuarios_service, inico_session_service
from schemas.esquemas import UsuarioCreate, UsuarioRead
from database.conexion import get_session


router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.post("/registrar")
def crear_usuario(data: UsuarioCreate, session: Session = Depends(get_session)):
    
    nuevo_usuario = crear_usuario_service(data, session)
    
    if isinstance(nuevo_usuario, dict):
            raise HTTPException(status_code=409, detail=nuevo_usuario["error"])
    
    return nuevo_usuario

@router.post("/login")
def inico_session(usuario: str, contrasena: str,  session: Session = Depends(get_session) ):
    
    inicio =  inico_session_service(usuario, contrasena, session)
    
    if isinstance(inicio, dict):
        raise HTTPException(status_code=401, detail=inicio["error"])
    
    return

@router.get("/", response_model=list[UsuarioRead])
def obtener_usuarios( session: Session = Depends(get_session)):
    return obtener_usuarios_service(session)

