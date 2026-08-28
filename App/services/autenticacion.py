# en este voy a poner los creacion de token y validaciones 
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone 

import jwt 


# Carga automáticamente las variables del archivo .env
load_dotenv()

# traemos los valores de codificacion de tokens desde el .env 
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# Aquí van las funciones:
# - create_access_token()
# - get_current_user()
# - require_roles()

#  se encarga de validar que el usuario exista verifica su username y su password en fake_users_db 
def authenticate_user(username: str, password: str, session ):
#  esto debe ser desde la db 
    user = fake_users_db.get(username)
    if user is None:
        return None
    
    if user["password"] != password:
        return None
    
    return user

# crea el token 
def create_access_token(data: dict): # recibe un diccionario con la informacion que se quiere integrar en el token 

    to_encode = data.copy()
    # porque tantos tipos de tiempo timedelta timezone datetime
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


