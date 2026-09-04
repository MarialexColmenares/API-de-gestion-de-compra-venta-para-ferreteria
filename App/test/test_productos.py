from fastapi.testclient import TestClient
from main import app
from services.autenticacion import crear_token

client = TestClient(app)

def test_utilidad_producto_con_rol_permitido():
    
    payload = {"sub": "usuario_prueba", "role": "admin", "id": 1}
    token = crear_token(data=payload)
    
    response = client.get("/productos/1/utilidad", headers={"Authorization": f"Bearer {token}"})
    
    # 1. Código de estado
    assert response.status_code == 200
    
    # 2. Estructura del JSON (Claves presentes)
    data = response.json()
    
    assert "producto" in data
    assert "costo" in data
    assert "precio" in data
    assert "utilidad" in data
    assert "margen_%" in data

def test_utilidad_producto_sin_token():
    
    response = client.get("/productos/1/utilidad")
    
    # 1. Código de estado
    assert response.status_code == 401
    
    # 2. Mensaje de error
    assert response.json() == {"detail": "Not authenticated"}


def test_utilidad_producto_con_rol_no_permitido():
    
    payload = {"sub": "usuario_prueba", "role": "gestor_stock", "id": 1}
    token = crear_token(data=payload)
    
    response = client.get("/productos/1/utilidad", headers={"Authorization": f"Bearer  {token}"})
    
    # 1. Código de estado
    assert response.status_code == 403
    
    # 2. Mensaje de error
    assert response.json() == {"detail": "No autorizado"}
