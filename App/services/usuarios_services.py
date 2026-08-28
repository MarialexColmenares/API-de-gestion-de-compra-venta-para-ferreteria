from sqlmodel import select
from models.modelos import Usuario
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def hashear_contrasena(contrasena: str):
    return pwd_context.hash(contrasena)

def verificar_contrasena(contrasena_ingresada: str, contrasena_hasheada: str):
    return pwd_context.verify(contrasena_ingresada, contrasena_hasheada)


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
    
    usuario_encontrado = session.exec(select(Usuario).where(Usuario.username == usuario)).first()
    
    if not usuario_encontrado:
        return {"error": "Error: no existe un usuario con ese username "}
    
    contrasena_correcta = verificar_contrasena(contrasena, usuario_encontrado.contrasena)
    
    if not contrasena_correcta:
        return {"error": "Error: la contrasena es incorrecta"}

    return {"autorizado":"inicio de session exitoso"}

def obtener_usuarios_service(session):

    return session.exec(select(Usuario)).all()

