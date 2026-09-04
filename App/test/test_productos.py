from fastapi.testclient import TestClient
from main import app
from services.autenticacion import crear_token

client = TestClient(app)

# comprueba que un usuario con rol permitido pueda acceder a las utilidades de un producto
def test_utilidad_producto_con_rol_permitido():
    
    payload = {"sub": "usuario_prueba", "role": "admin", "id": 1}
    token = crear_token(data=payload)
    
    response = client.get("/productos/1/utilidad", headers={"Authorization": f"Bearer {token}"})
    
    # Código de estado
    assert response.status_code == 200
    
    #  Estructura del JSON (Claves presentes)
    data = response.json()
    
    assert "producto" in data
    assert "costo" in data
    assert "precio" in data
    assert "utilidad" in data
    assert "margen_%" in data

# comprueba que un usuario sin token no pueda acceder a las utilidades de un producto
def test_utilidad_producto_sin_token():
    
    response = client.get("/productos/1/utilidad")
    
    # Código de estado
    assert response.status_code == 401
    
    #  Mensaje de error
    assert response.json() == {"detail": "Not authenticated"}

# comprueba que un usuario con rol no permitido no pueda acceder a las utilidades de un producto
def test_utilidad_producto_con_rol_no_permitido():
    
    payload = {"sub": "usuario_prueba", "role": "gestor_stock", "id": 1}
    token = crear_token(data=payload)
    
    response = client.get("/productos/1/utilidad", headers={"Authorization": f"Bearer  {token}"})
    
    #  Código de estado
    assert response.status_code == 403
    
    #  Mensaje de error
    assert response.json() == {"detail": "No autorizado"}
