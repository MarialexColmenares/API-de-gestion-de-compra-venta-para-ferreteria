from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from services.usuarios_services import crear_usuario_service, obtener_usuarios_service, inico_session_service, desactivar_usuario_service
from services.autenticacion import get_current_user, require_roles
from schemas.esquemas import UsuarioCreate, UsuarioRead
from database.conexion import get_session
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.post("/registrar")
def crear_usuario(data: UsuarioCreate, session: Session = Depends(get_session)):
    
    nuevo_usuario = crear_usuario_service(data, session)
    
    if isinstance(nuevo_usuario, dict):
            raise HTTPException(status_code=409, detail=nuevo_usuario["error"])
    
    return nuevo_usuario

@router.post("/login")
def inico_session(form_data: OAuth2PasswordRequestForm = Depends(),  session: Session = Depends(get_session) ):
    
    inicio =  inico_session_service(form_data.username, form_data.password, session)
    
    if inicio == None:
        raise HTTPException(status_code=401, detail="credenciales de inicio de session incorrectas")
    
    return inicio 

@router.get("/", response_model=list[UsuarioRead])
def obtener_usuarios( session: Session = Depends(get_session), current_user: dict = Depends(require_roles("admin"))):
    return obtener_usuarios_service(session)

@router.get("/perfil")
def ver_perfil(current_user: dict = Depends(get_current_user)):
    return {"usuario": current_user}

@router.delete("/eliminar/{id_user}")
def desactivar_usuario(id_user: int, session: Session = Depends(get_session), current_user: dict = Depends(require_roles("admin"))):
    
    user = desactivar_usuario_service(id_user, session)
    
    if user == None:
        raise HTTPException(status_code=404, detail="El usuario a desactivar no existe")
    
    return f"Usuario {user.username} desactivado"