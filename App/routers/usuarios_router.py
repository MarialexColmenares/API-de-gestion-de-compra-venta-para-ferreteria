from fastapi import APIRouter, Depends
from sqlmodel import Session
from services.usuarios_services import crear_usuario_service, obtener_usuarios_service
from schemas.esquemas import UsuarioCreate
from database.conexion import get_session


router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.post("")
def crear_usuario(data: UsuarioCreate, session: Session = Depends(get_session)):
    return crear_usuario_service(data, session)

@router.get("/")
def obtener_usuarios( session: Session = Depends(get_session)):
    return obtener_usuarios_service(session)

