from fastapi import APIRouter, Depends, HTTPException
from database.conexion import get_session
from sqlmodel import Session
from schemas.esquemas import ProveedorCreate, ProveedorRead, ProveedorUpdate, CompraRead
from typing import List
from services.proveedores_services import *

router = APIRouter(prefix="/proveedores", tags=["Proveedores"])

# crear proveedor
@router.post("/", response_model=ProveedorRead)
def crear_proveedor(data: ProveedorCreate, session: Session = Depends(get_session)):
    
    nuevo_proveedor = crear_proveedor_service(data, session)
    if not nuevo_proveedor:
        raise HTTPException(status_code=409, detail="Correo ya registrado")
    
    return nuevo_proveedor

#  proveedores activos 
@router.get("/activos", response_model=List[ProveedorRead])
def proveedores_activos(session: Session = Depends(get_session)):
    
    proveedores = proveedores_activos_service(session)
    
    if not proveedores:
        raise HTTPException(
            status_code=404,
            detail="No hay Proveedores activos por el momento") 
    
    return proveedores

# obtener todos los proveedores
@router.get("/", response_model=List[ProveedorRead])
def listar_proveedores(session: Session = Depends(get_session)):
    
    proveedores = obtener_proveedores_service(session)
    
    if not proveedores:
        raise HTTPException(status_code=404, detail=f"Aun no hay registros de proveedores")
    
    return proveedores

# obtener por id
@router.get("/{proveedor_id}", response_model=ProveedorRead)
def obtener_proveedor(proveedor_id: int, session: Session = Depends(get_session)):
    
    proveedor = obtener_proveedor_service(proveedor_id, session)
    
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    
    return proveedor

# actualizacion parcial
@router.patch("/{proveedor_id}", response_model=ProveedorRead)
def editar_proveedor(proveedor_id: int, data: ProveedorUpdate, session: Session = Depends(get_session)):

    proveedor_db = editar_proveedor_service(proveedor_id, data, session)
    if not proveedor_db:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    
    return proveedor_db

# eliminacion logica (desactivar proveedor)
@router.delete("/{proveedor_id}")
def eliminar_proveedor(proveedor_id: int, session: Session = Depends(get_session)):
    
    proveedor_db = cambiar_estado_proveedor_service(proveedor_id, False, session)
    if not proveedor_db:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    
    return {"message": f"Proveedor {proveedor_db.nombre_empresa} desactivado"}

# activar proveedor (revertir desactivacion)
@router.patch("/activar/{proveedor_id}")
def activar_proveedor(proveedor_id: int, session: Session = Depends(get_session)):
    proveedor_db = cambiar_estado_proveedor_service(proveedor_id, True, session)
    
    if not proveedor_db:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    
    
    return {"message": f"Proveedor {proveedor_db.nombre_empresa} activado"}

# obtener por nombre
@router.get("/filtro/{nombre}", response_model=List[ProveedorRead])  # Ruta clara
def buscar_proveedores_por_nombre(nombre: str, session: Session = Depends(get_session)):
    
    proveedores = buscar_proveedores_service(nombre, session)
    
    if not proveedores:
        raise HTTPException(status_code=404, detail=f"No se encontraron proveedores: {nombre}")
    
    return proveedores

# compras d¿con un proveedor
@router.get("/{proveedor_id}/compras", response_model=List[CompraRead])
def compras_proveedor(proveedor_id: int, session: Session = Depends(get_session)):
    
    proveedor, compras = compras_proveedor_service(proveedor_id, session)
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    
    if not compras:
        raise HTTPException(status_code=404, detail="No se encontraron compras a este proveedor ")
    
    return compras
