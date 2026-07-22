from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import Optional
from typing import List

from schemas.esquemas import AlmacenCreate, AlmacenRead, AlmacenUpdate, ProductoRead, AsignarProductoAlmacen
from database.conexion import get_session


from services.almacen_service import *

router = APIRouter(prefix="/almacenes", tags=["Almacenes"])

# crear un nuevo almacen
@router.post("/", response_model=AlmacenRead)
def crear_almacen(data: AlmacenCreate, session: Session = Depends(get_session)):
    
    nuevo_almacen = crear_almacen_service(data, session)
    
    if nuevo_almacen == None:
        raise HTTPException(
            status_code=400, 
            detail=f"Ya existe un almacén llamado '{data.nombre}'"
        )

    return nuevo_almacen

# obtener todos los almacenes
@router.get("/", response_model=List[AlmacenRead])
def obtener_almacenes(session: Session = Depends(get_session)):
    
    almacenes = obtener_almacenes_service(session)
    
    # se evalua si se devolvio una lista de almacenes
    if not almacenes:
        raise HTTPException(
            status_code=404,
            detail="No se encontraron Almacenes"
        )
    
    return almacenes

# obtener solo los almacenes activos (estado=True)
@router.get("/activos", response_model=List[AlmacenRead])
def almacenes_activas(session: Session = Depends(get_session)):
    
    almacenes = almacenes_activas_service(session)
    
    if not almacenes:
        raise HTTPException(
            status_code=404,
            detail="No hay Almacenes activos por el momento") 
    
    return almacenes

# obtener almacenes por ubicacion
@router.get("/filtros", response_model=List[AlmacenRead])
def buscar_almacenes(
    #  filtro opcionales
    nombre: Optional[str] = None,
    ubicacion: Optional[str] = None,
    estado: Optional[bool] = None,
    session: Session = Depends(get_session)):
    
    # evaluamos que el usuario hay enviado por lo menos un filtro 
    if not nombre and not ubicacion and estado is None:
        raise HTTPException(
            status_code=400, 
            detail="Debes proporcionar al menos un parámetro de búsqueda (nombre, ubicación o estado)."
        )
    
    almacenes = buscar_almacenes_service(session, nombre, ubicacion, estado)
    
    # evaluemos no haber recivido una lista vacia y enviamos error
    if not almacenes:
        raise HTTPException(
            status_code=404,
            detail="No se encontraron almacenes por los filtros")
        
    return almacenes

# obtener un almacen por su ID
@router.get("/{almacen_id}", response_model=AlmacenRead)
def obtener_almacen(almacen_id: int, session: Session = Depends(get_session)):
    
    almacen = obtener_almacen_service(almacen_id, session)
    
    if almacen == None:
        raise HTTPException(
            status_code=404, 
            detail=f"Almacén con ID {almacen_id} no encontrado")
    
    return almacen

# eliminar un almacen (cambio de estado a False)
@router.delete("/{almacen_id}")
def desactivar_almacen(almacen_id: int, session: Session = Depends(get_session)):
    
    almacen = desactivar_almacen_service(almacen_id, session)
    
    # evaluamos si la funcion retorno None 
    if almacen == None:
        raise HTTPException(
            status_code=404, 
            detail=f"Almacen con ID {almacen_id} no encontrado")

    # retornamos mensaje de confirmacion de eliminacion 
    return {"mensaje": f"Almacén con ID {almacen_id} ha sido eliminado (estado cambiado a False)"}

# activar almacen 
@router.patch("/activar")
def activar_almacen(almacen_id: int, session: Session = Depends(get_session)):
    
    almacen = activar_almacen_service(almacen_id, session)
    
    if almacen == None:
        raise HTTPException(
            status_code=409, detail=f"Almacen con ID {almacen_id} no encontrado")
        
    
    return {"mensaje": f"Almacén con ID {almacen_id} ha sido activado (estado cambiado a True)"}

# actualizacion parcial de almacen
@router.patch("/{almacen_id}")
def actualizar_parcial_almacen(almacen_id:int, data:AlmacenUpdate, session:Session = Depends(get_session)):
    
    almacen = actualizar_parcial_almacen_service(almacen_id, data, session)
    
    if almacen == None:
        raise HTTPException(
            status_code=404, 
            detail=f"Almacen con ID {almacen_id} no encontrado")
        
    return almacen


@router.post("/asignar-producto")
def asignar_producto_a_almacen(data: AsignarProductoAlmacen, session: Session = Depends(get_session)):
    
    if data.cantidad < 0:
        raise HTTPException(status_code=400, detail="agrega al menos un producto al almacen ")
    
    nuevo_producto = asignar_producto_a_almacen_service(data, session)
    
    if nuevo_producto == None:
        raise HTTPException(status_code=404, detail="Producto o Almacén no encontrado")
    
    return nuevo_producto
   

# inventario de un almacen específico
@router.get("/{almacen_id}/inventario", response_model=List[ProductoRead])
def ver_inventario_almacen(almacen_id: int, session: Session = Depends(get_session)):
    
    # utilizamos la funcion de obtener almacen para seleccionar el almacen con el id que envia el usuario
    almacen = obtener_almacen_service(almacen_id, session)

    # evaluamos si la funcion retorno None
    if almacen == None :
        raise HTTPException(status_code=404, detail="Almacén no encontrado")
    
    # si el almacen existe usamos la funcion ver inventario para traer los productos en ese almacen
    productos = ver_inventario_almacen_service(almacen)
    
    # evaluamos si no devuelve una lista de productos 
    if not productos:
        raise HTTPException(status_code=404, detail=f"Aun no hay productos en el almacen {almacen.nombre}")
    
    return productos

