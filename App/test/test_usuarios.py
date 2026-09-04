from fastapi.testclient import TestClient
from main import app

from services.autenticacion import crear_token

client = TestClient(app)

# comprueba que un usuario con rol permitido pueda acceder a los usuarios del sistema
def test_obtener_usuarios():
    
    payload = {"sub": "usuario_prueba", "role": "admin", "id": 1}
    
    token = crear_token(data=payload)
    
    response = client.get("/usuarios/", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    
#  comprueba que un usuario sin token no pueda acceder a los usuarios del sistema
def test_obtener_usuarios_sin_token():
     
    response = client.get("/usuarios/")
    
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
    
#  comprueba que no se pueda registrar un usuario duplicado
def test_registro_usuario_duplicado():
    # definimos los datos para registrar un usuario que ya existe
    usuario_data = {
        "username": "usuario_prueba",
        "contrasena": "contrasena_segura",
        "rol": "admin"
    }
        
    # Registramos el usuario duplicado
    response_registro = client.post("/usuarios/registrar", json=usuario_data)
    assert response_registro.status_code == 409
           
#  comprueba un inico de session exitoso
def test_inicio_session():
    
    # usamos el mismo usuario de la prueba anterior para iniciar sesión
    login_data = {
        "username": "usuario_prueba",
        "password": "contrasena_segura"
    }
    
    response_login = client.post("/usuarios/login", data=login_data)
    
    assert response_login.status_code == 200
    assert "access_token" in response_login.json()
    
#  comprueba un inicio de session fallido con credenciales incorrectas
def test_inicio_session_incorrecto():
    
    # Intentamos iniciar sesión con credenciales incorrectas 
    login_data = {
        "username": "usuario_inexistente",
        "password": "contrasena_incorrecta"
    }
    
    response_login = client.post("/usuarios/login", data=login_data)
    
    assert response_login.status_code == 401
    assert response_login.json() == {"detail": "credenciales de inicio de session incorrectas"}
    