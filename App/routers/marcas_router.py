from fastapi import APIRouter, Depends, HTTPException
from database.conexion import get_session
from sqlmodel import Session
from schemas.esquemas import MarcaRead, MarcaCreate, ProductoRead, MarcaUpdate
from typing import List
from services.marcas_services import *
from services.autenticacion import get_current_user, require_roles


router = APIRouter(prefix="/marcas", tags=["Marcas"])

# crear marca
@router.post("/", response_model=MarcaRead)
def crear_marca(data : MarcaCreate,session: Session = Depends(get_session), current_user: dict = Depends(require_roles("admin", "gestor_stock"))):
    
    nueva_marca = crear_marca_service(data, session)
    
    if nueva_marca == None:
        raise HTTPException(
            status_code=409,
            detail=f" La marca {data.nombre} ya fue registrada")
    
    return nueva_marca

#obtener todas las marcas 
@router.get("/", response_model=List[MarcaRead])
def obtener_marcas(session: Session = Depends(get_session), current_user: dict = Depends(require_roles("admin"))):
    
    marcas = obtener_marcas_service(session)
    
    if not marcas:
        raise HTTPException(
            status_code=404,
            detail="No se encontraron registros de marcas en la db")
    
    return marcas

@router.get("/activas", response_model=List[MarcaRead])
def obtener_marcas_activas(session: Session = Depends(get_session), current_user: dict = Depends(get_current_user)):
    
    marcas = obtener_marcas_activas_service(session)
    
    if not marcas:
        raise HTTPException(
            status_code=404,
            detail="No se encontraron registros de marcas en la db")
        
    return marcas

# buscar marca por nombre
@router.get("/por/{nombre}", response_model=List[MarcaRead])
def buscar_marcas(nombre: str, session: Session = Depends(get_session), current_user: dict = Depends(get_current_user)):
    
    marca = buscar_marcas_service(nombre, session)
    if not marca:
        raise HTTPException(
            status_code=404, 
            detail=f"Marca con nombre '{nombre}' no encontrada")
    
    return marca

# obtener una marca por ID
@router.get("/{marca_id}", response_model=MarcaRead)
def obtener_marca(marca_id: int, session: Session = Depends(get_session), current_user: dict = Depends(get_current_user)):
    marca = obtener_marca_service(marca_id, session)
    
    if not marca:
            raise HTTPException(
                status_code=404, 
                detail=f"Marca con ID {marca_id} no encontrada")
    return marca

# actualizacion parcial
@router.patch("/{marca_id}", response_model=MarcaRead)
def actualizar_marca(marca_id: int, data: MarcaUpdate, session: Session = Depends(get_session), current_user: dict = Depends(require_roles("admin", "gestor_stock"))):
    marca = actualizar_marca_service(marca_id, data, session)
    
    if not marca:
        raise HTTPException(
            status_code=404, 
            detail=f"Marca con ID {marca_id} no encontrada")
        
    return marca

#  eliminacion logica de marca
@router.delete("/{marca_id}")
def desactivar_marca(marca_id: int, session: Session = Depends(get_session), current_user: dict = Depends(require_roles("admin", "gestor_stock"))):
    
    marca = desactivar_marca_service(marca_id, session)
    
    if not marca:
        raise HTTPException(
            status_code= 404, 
            detail="Marca no encontrada")
    
    # evaluamos si la funcion devolvio un diccionario de error
    if isinstance(marca, dict) and "error" in marca:
        raise HTTPException(
            status_code=400, 
            detail=marca["error"])

    return {"message": f"Marca con ID {marca_id} ha sido eliminada (estado cambiado a False)"}

# activacion de marca
@router.patch("/{marca_id}/activar")
def activar_marca(marca_id: int, session: Session = Depends(get_session), current_user: dict = Depends(require_roles("admin")) ):
    marca = activar_marca_service(marca_id, session)
    
    if not marca:
        raise HTTPException(
            status_code= 404, 
            detail="Marca no encontrada")
    
    return {"message": f"Marca con ID {marca_id} ha sido activada (estado cambiado a True)"}

#  contar productos por marca 
@router.get("/{marca_id}/estadisticas")
def obtener_estadisticas_marca(marca_id: int, session: Session = Depends(get_session), current_user: dict = Depends(get_current_user)):
    estadisticas = obtener_estadisticas_marca_service(marca_id, session)
    if not estadisticas:
        raise HTTPException(status_code=404, detail="Marca no encontrada")
    return estadisticas


# 3. NUEVO ENDPOINT MEJORADO (Idea extra)
@router.get("/{marca_id}/productos", response_model=List[ProductoRead])
def productos_de_marca(marca_id: int, session: Session = Depends(get_session), current_user: dict = Depends(get_current_user)):
    
    marca = obtener_marca_service(marca_id, session)
    
    if not marca:
        raise HTTPException(status_code=404, detail="no se encontro la marca")
    
    productos = productos_de_marca_service(marca_id, session)
    
    if not productos:
        raise HTTPException(status_code=404, detail=f"No existen productos de la marca {marca.nombre}")
    
    return productos