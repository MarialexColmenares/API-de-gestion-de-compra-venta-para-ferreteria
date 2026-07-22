from fastapi import APIRouter, Depends, HTTPException, status
from database.conexion import engine, get_session
from sqlmodel import Session, select
from models.modelos import Marca, Producto
from schemas.esquemas import MarcaRead, MarcaCreate, ProductoRead, MarcaUpdate
from typing import List


router = APIRouter(prefix="/marcas", tags=["Marcas"])

# crear marca
@router.post("/", response_model=MarcaRead)
def crear_marca(data : MarcaCreate,session: Session = Depends(get_session)):
    
    statement = select(Marca).where(Marca.nombre == data.nombre)
    existe = session.exec(statement).first()
    
    if existe:
        raise HTTPException(
            status_code=409,
            detail=f" La marca {data.nombre} ya fue registrada")
    
    nueva_marca = Marca(
        nombre=data.nombre,
        estado=data.estado)
    
    session.add(nueva_marca)
    session.commit()
    session.refresh(nueva_marca)
    
    return nueva_marca

#obtener todas las marcas 
@router.get("/", response_model=List[MarcaRead])
def obtener_marcas(session: Session = Depends(get_session)):
    
    marcas = session.exec(select(Marca)).all()
    
    if not marcas:
        raise HTTPException(
            status_code=404,
            detail="No se encontraron registros de tablas en la db")
    
    return marcas

# buscar marca por nombre
@router.get("/por/{nombre}", response_model=List[MarcaRead])
def buscar_marcas(nombre: str, session: Session = Depends(get_session)):
    
    statement = select(Marca).where(Marca.nombre.contains(nombre))
    marca = session.exec(statement).all()
    if not marca:
        raise HTTPException(
            status_code=404, 
            detail=f"Marca con nombre '{nombre}' no encontrada")
    
    return marca

# obtener una marca por ID
@router.get("/{marca_id}", response_model=MarcaRead)
def obtener_marca(marca_id: int, session: Session = Depends(get_session)):
    marca = session.get(Marca, marca_id)
    
    if not marca:
            raise HTTPException(
                status_code=404, 
                detail=f"Marca con ID {marca_id} no encontrada")
    return marca

# actualizacion parcial
@router.patch("/{marca_id}", response_model=MarcaRead)
def actualizar_marca(marca_id: int, data: MarcaUpdate, session: Session = Depends(get_session)):
    marca = session.get(Marca, marca_id)
    
    if not marca:
        raise HTTPException(
            status_code=404, 
            detail=f"Marca con ID {marca_id} no encontrada")
        
    if data.nombre is not None:
        marca.nombre = data.nombre
    
    session.commit()
    session.refresh(marca)
    
    return marca

#  eliminacion logica de marca
@router.delete("/{marca_id}")
def desactivar_marca(marca_id: int, session: Session = Depends(get_session)):
    marca = session.get(Marca, marca_id)
    
    if not marca:
        raise HTTPException(
            status_code= 404, 
            detail="Marca no encontrada")
        
    # Si la marca tiene productos, no permitimos la desactivación simple
    conteo = len(marca.productos)
    if conteo > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"No se puede desactivar '{marca.nombre}' porque tiene {conteo} productos vinculados")
    
    marca.estado = False
    
    session.commit()

    return {"message": f"Marca con ID {marca_id} ha sido eliminada (estado cambiado a False)"}

# activacion de marca
@router.patch("/{marca_id}/activar")
def activar_marca(marca_id: int, session: Session = Depends(get_session) ):
    marca = session.get(Marca, marca_id)
    
    if not marca:
        raise HTTPException(
            status_code= 404, 
            detail="Marca no encontrada")
    
    marca.estado = True
    
    session.commit()

    return {"message": f"Marca con ID {marca_id} ha sido activada (estado cambiado a True)"}

#  contar productos por marca 
@router.get("/{marca_id}/estadisticas")
def obtener_estadisticas_marca(marca_id: int, session: Session = Depends(get_session)):
    marca = session.get(Marca, marca_id)
    if not marca:
        raise HTTPException(status_code=404, detail="Marca no encontrada")
    
    conteo = len(marca.productos)
    
    return {
        "marca": marca.nombre,
        "total_productos_asociados": conteo,
        "estado": "Activa" if marca.estado else "Inactiva"}


# 3. NUEVO ENDPOINT MEJORADO (Idea extra)
@router.get("/{marca_id}/productos", response_model=List[ProductoRead])
def productos_de_marca(marca_id: int, session: Session = Depends(get_session)):
    marca = session.get(Marca, marca_id)
    if not marca:
        raise HTTPException(status_code=404, detail="Marca no encontrada")
    
    statement = select(Producto).where(
        Producto.marca_id == marca_id,
        Producto.estado == True
    )
    productos = session.exec(statement).all()
    
    if not productos:
        raise HTTPException(status_code=404, detail=f"No existen productos de la marca {marca.nombre}")
    
    return productos