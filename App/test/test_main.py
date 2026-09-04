from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

#  comprueba que la api haya iniciado correctamente y que la ruta raíz devuelva el mensaje de bienvenida esperado
def test_root():
    response = client.get("/")
    
    assert response.status_code == 200
    assert response.json() == {"Bienvenidos": "Sistema de Centro de Repuestos y Ferretería"}