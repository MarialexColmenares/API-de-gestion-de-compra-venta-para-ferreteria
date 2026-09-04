# en este voy a poner los creacion de token y validaciones 
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone 

import jwt 
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError

from sqlmodel import select
from models.modelos import Usuario

from passlib.context import CryptContext

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="usuarios/login")

# Carga automáticamente las variables del archivo .env
load_dotenv()

# traemos los valores de codificacion de tokens desde el .env 
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(30)

# para el hasheo de contraseñas 
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def hashear_contrasena(contrasena: str):
    return pwd_context.hash(contrasena)

def verificar_contrasena(contrasena_ingresada: str, contrasena_hasheada: str):
    return pwd_context.verify(contrasena_ingresada, contrasena_hasheada)

#  se encarga de validar que el usuario exista verifica su username y su password en fake_users_db 
def authenticate_user(username: str, password: str, session ):

    user = session.exec(select(Usuario).where(Usuario.username == username)).first()
    if user is None:
        return None
    
    contrasena_verificada = verificar_contrasena(password, user.contrasena)
    if not contrasena_verificada:
        return None
    
    return user 

# crea el token 
def crear_token(data: dict): # recibe un diccionario con la informacion que se quiere integrar en el token 

    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})
    token = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    
    return token

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        # Decodifica el token usando la clave secreta y el algoritmo
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        
        username = payload.get("sub")
        role = payload.get("role")
        id = payload.get("id")
        
        # Evalúa si faltan datos requeridos en el payload
        if username is None or role is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Token inválido"
            )
        
        return {
            "username": username,
            "role": role,
            "id": id
        }
    
    except ExpiredSignatureError:
        # 1. Captura cuando el token sobrepasa el tiempo límite (exp)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="El token ha expirado"
        )
    except InvalidTokenError:
        # 2. Captura firma alterada, datos corruptos o formato incorrecto
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="No se pudo validar el token"
        )
    
def require_roles(*allowed_roles: str):
    
    def checker(current_user: dict = Depends(get_current_user)):
        
        if current_user["role"] not in allowed_roles:
            
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
        
        return current_user
    
    return checker