from sqlmodel import select
from models.modelos import Usuario
from passlib.context import CryptContext

def crear_usuario_service(data, session):
    
    if session.exec(select(Usuario).where(Usuario.username == data.username)).first():
        return {"error": "Error: Ya existe un usuario con ese username"}
    
    if len(data.contrasena) <= 8:
        return {"error": "Error: la contraseña debe tener mas de 8 caracteres"}

    
    nuevo_usuario = Usuario(
        username = data.username,
        contrasena = data.contrasena,
        rol = data.rol
    )
    
    session.add(nuevo_usuario)
    session.commit()
    session.refresh(nuevo_usuario)
    
    return nuevo_usuario

def obtener_usuarios_service(session):

    return session.exec(select(Usuario)).all()