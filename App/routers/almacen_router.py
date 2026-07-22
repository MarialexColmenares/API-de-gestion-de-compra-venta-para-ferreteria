from fastapi import APIRouter, Depends, HTTPException, status
from database.conexion import engine, get_session
from sqlmodel import Session, select
from models.modelos import Almacen, Producto, ProductoAlmacen
from schemas.esquemas import AlmacenCreate, AlmacenRead, AlmacenUpdate, ProductoRead, AsignarProductoAlmacen
from typing import Optional
from typing import List
from sqlalchemy import func

router = APIRouter(prefix="/almacenes", tags=["Almacenes"])

# crear un nuevo almacen
@router.post("/", response_model=AlmacenRead)
def crear_almacen(data: AlmacenCreate,session: Session = Depends(get_session)):
    
    statement = select(Almacen).where(func.lower(Almacen.nombre) == data.nombre.lower())
    almacen_existente = session.exec(statement).first()
    
    if almacen_existente:
        raise HTTPException(
            status_code=400, 
            detail=f"Ya existe un almacén registrado con el nombre: {data.nombre}"
        )

    nuevo_almacen = Almacen(
        nombre=data.nombre,
        ubicacion=data.ubicacion,
        estado=data.estado)
    

    session.add(nuevo_almacen)
    session.commit()
    session.refresh(nuevo_almacen)
    
    return nuevo_almacen

# obtener todos los almacenes
@router.get("/", response_model=List[AlmacenRead])
def obtener_almacenes(session: Session = Depends(get_session)):
    
    almacenes = session.exec(select(Almacen)).all()
    
    if not almacenes: 
        raise HTTPException(
            status_code=404,
            detail="No se encontraron Almacenes"
        )
    return almacenes

# obtener solo los almacenes activos (estado=True)
@router.get("/activos", response_model=List[AlmacenRead])
def almacenes_activas(session: Session = Depends(get_session)):
    
    statement = select(Almacen).where(Almacen.estado == True)
    almacenes = session.exec(statement).all()
    
    if not almacenes:
        raise HTTPException(
            status_code=404,
            detail="No hay Almacenes activos por el momento") 
    
    return almacenes

# obtener almacenes por ubicacion
@router.get("/ubicacion", response_model=List[AlmacenRead])
def obtener_ubicacion_almacenes(ubicacion: str, session: Session = Depends(get_session)):
    
    statement = select(Almacen).where( Almacen.ubicacion.contains(ubicacion))
    almacenes = session.exec(statement).all()
    
    if not almacenes:
        raise HTTPException(
            status_code=404,
            detail="No se encontraron almacenes en esa zona")
        
    return almacenes

# obtener un almacen por su ID
@router.get("/{almacen_id}", response_model=AlmacenRead)
def obtener_almacen(almacen_id: int, session: Session = Depends(get_session)):
    
    almacen = session.get(Almacen, almacen_id)
    
    if not almacen:
        raise HTTPException(
            status_code=404, 
            detail=f"Almacén con ID {almacen_id} no encontrado")
    
    return almacen

# eliminar un almacen (cambio de estado a False)
@router.delete("/{almacen_id}")
def desactivar_almacen(almacen_id: int, session: Session = Depends(get_session)):
    almacen = session.get(Almacen, almacen_id)
    
    if not almacen:
        raise HTTPException(
            status_code=404, 
            detail=f"Almacen con ID {almacen_id} no encontrado")

    almacen.estado = False
    
    session.add(almacen)
    session.commit()
    
    return {"mensaje": f"Almacén con ID {almacen_id} ha sido eliminado (estado cambiado a False)"}

# activar almacen 
@router.patch("/activar")
def activar_almacen(almacen_id: int, session: Session = Depends(get_session)):
    
    almacen = session.get(Almacen, almacen_id)
    
    if not almacen:
        raise HTTPException(
            status_code=409, detail=f"Almacen con ID {almacen_id} no encontrado")
        
    almacen.estado = True
    
    session.add(almacen)
    session.commit()
    session.refresh(almacen)
    
    return {"mensaje": f"Almacén con ID {almacen_id} ha sido activado (estado cambiado a True)"}

# actualizacion parcial de almacen
@router.patch("/{almacen_id}")
def actualizar_parcial_almacen(almacen_id: int,almacen_data: AlmacenUpdate,session: Session = Depends(get_session)):
    
    almacen_db = session.get(Almacen, almacen_id)
    
    if not almacen_db:
        raise HTTPException(
            status_code=404, 
            detail=f"Categoría con ID {almacen_id} no encontrada")
        
    if almacen_data.nombre is not None:
        almacen_db.nombre = almacen_data.nombre
    if almacen_data.ubicacion is not None:
        almacen_db.ubicacion = almacen_data.ubicacion

    session.add(almacen_db)
    session.commit()
    session.refresh(almacen_db)
    
    return almacen_db


@router.post("/asignar-producto")
def asignar_producto_a_almacen(data: AsignarProductoAlmacen, session: Session = Depends(get_session)):
    # 1. Validar que existan ambos
    producto = session.get(Producto, data.producto_id)
    almacen = session.get(Almacen, data.almacen_id)
    
    if not producto or not almacen:
        raise HTTPException(status_code=404, detail="Producto o Almacén no encontrado")

    # 2. Verificar si ya existe el producto en ese almacén
    statement = select(ProductoAlmacen).where(
        ProductoAlmacen.producto_id == data.producto_id,
        ProductoAlmacen.almacen_id == data.almacen_id)
    existente = session.exec(statement).first()

    if existente:

        existente.cantidad += data.cantidad
        session.add(existente)
    else:

        nuevo_vinculo = ProductoAlmacen(
            producto_id=data.producto_id,
            almacen_id=data.almacen_id,
            cantidad=data.cantidad
        )
        session.add(nuevo_vinculo)

    # 3. Actualizar el stock total global del producto
    producto.stock_total += data.cantidad
    session.add(producto)
    
    session.commit()
    return {"mensaje": f"Se agregaron {data.cantidad} unidades de '{producto.nombre}' al almacén '{almacen.nombre}'"}

# inventario de un almacen específico
@router.get("/{almacen_id}/inventario", response_model=List[ProductoRead])
def ver_inventario_almacen(almacen_id: int, session: Session = Depends(get_session)):
    
    almacen = session.get(Almacen, almacen_id)
    
    if not almacen:
        raise HTTPException(status_code=404, detail="Almacén no encontrado")
    
    productos = almacen.productos
    
    if not productos:
        raise HTTPException(status_code=404, detail=f"Aun no hay productos en el almacen {almacen.nombre}")
    
    return 

