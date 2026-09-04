from sqlmodel import select
from models.modelos import Usuario
from services.autenticacion import authenticate_user, hashear_contrasena, crear_token

def crear_usuario_service(data, session):
    
    if session.exec(select(Usuario).where(Usuario.username == data.username)).first():
        return {"error": "Error: Ya existe un usuario con ese username"}
    
    contrasena_hash = hashear_contrasena(data.contrasena)

    nuevo_usuario = Usuario(
        username = data.username,
        contrasena = contrasena_hash,
        rol = data.rol
    )
    
    session.add(nuevo_usuario)
    session.commit()
    session.refresh(nuevo_usuario)
    
    return "usuario registrado correctamente"

def inico_session_service(usuario, contrasena, session):
    
    user = authenticate_user(usuario, contrasena, session)
    
    if user == None:
        return user

    access_token = crear_token(
        data={
            "sub": user.username,
            "role": user.rol,
            "id": user.id
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

def obtener_usuarios_service(session):

    return session.exec(select(Usuario)).all()

def desactivar_usuario_service(id_user, session):
    
    user_db = session.get(Usuario, id_user)
    if not user_db:
        return None

    user_db.estado = False
    
    session.add(user_db)
    session.commit()
    
    return user_db
