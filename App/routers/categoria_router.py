from fastapi import APIRouter, Depends, HTTPException, status
from database.conexion import get_session
from sqlmodel import Session
from models.modelos import Categoria
from schemas.esquemas import CategoriaCreate, CategoriaRead, ProductoRead, CategoriaUpdate
from typing import List

from services.categoria_services import * 

# prefix y tags para organizar las rutas de categoría en la documentación de FastAPI
router = APIRouter(prefix="/categorias", tags=["Categorías"])

#  crea una categoria nueva
@router.post("/", response_model=CategoriaRead)
def crear_categoria(data: CategoriaCreate, session: Session = Depends(get_session)):
    
    nueva_categoria = crear_categoria_service(data, session)
    
    # avaluamos si la funcion retorno None
    if nueva_categoria == None:
        raise HTTPException(status_code=409, detail="Ya existe una categoría con este nombre")

    return nueva_categoria

#  todas las categorias
@router.get("/", response_model=List[CategoriaRead])
def obtener_categorias(session: Session = Depends(get_session)):
    
    # llamamos a la funcion para obtener todas las categorias
    categorias = obtener_categorias_service(session)
    
    # evaluamos si no devolvio una lista de categorias
    if not categorias:
        raise HTTPException(
            status_code=404,
            detail="No se encontraron categorias en la base de datos")
        
    return categorias

# mostrar categorias activas 
@router.get("/activas", response_model=List[CategoriaRead])
def categorias_activas(session: Session = Depends(get_session)):
    
    categorias = categorias_activas_service(session)
    
    # evaluamos si se encontraron categorias activas
    if not categorias:
        raise HTTPException(status_code=404, detail="No se encontraron categorias activas")
    
    return categorias

# obtenemos una categoria por su id
@router.get("/{categoria_id}", response_model=CategoriaRead)
def obtener_categoria(categoria_id: int, session: Session = Depends(get_session)):
    
    categoria = obtener_categoria_service(categoria_id, session)
    
    # evaluamos si la funcion no retorno una categoria
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Categoría con ID {categoria_id} no encontrada")
    
    return categoria

#  eliminacion logica de categoria
@router.delete("/{categoria_id}")
def desactivar_categoria(categoria_id: int, session: Session = Depends(get_session)):
    
    categoria = desactivar_categoria_service(categoria_id, session)
    
    #  evaluamos si la funcion retorna None y lanzamos error 
    if categoria == None:
        raise HTTPException(status_code= 404,  detail="Categoría no encontrada")
    
    # se retorna nensaje de confirmacion de eliminacion logica
    return {"message": f"Categoría con ID {categoria_id} ha sido desactivada (estado cambiado a False)"}

#  reactivar categoria
@router.patch("/{categoria_id}/activar")
def activar_categoria(categoria_id: int, session: Session = Depends(get_session)):
    
    categoria = activar_categoria_service(categoria_id, session)
    
    if categoria == None:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    return {"message": f"Categoría '{categoria.nombre}' activada nuevamente"}

# actualizacion parcial
@router.patch("/{categoria_id}", response_model=CategoriaRead)
def editar_categoria(categoria_id: int, data: CategoriaUpdate, session: Session = Depends(get_session)):
    
    categoria = editar_categoria_service(categoria_id, data, session)
    
    if categoria == None:
        raise HTTPException(
            status_code=404, 
            detail=f"Categoría con ID {categoria_id} no encontrada")

    return categoria

# productos por categoria 
@router.get("/{nombre_categoria}/productos", response_model=List[ProductoRead])
def buscar_productos_por_categoria(categoria_id: int, session: Session = Depends(get_session)):
    
    # usamos la funcion de obtener categoria para obtener la categoria atraves de su id 
    categoria = obtener_categoria_service(categoria_id, session)

    # evaluamos si no retorno una categoria
    if not categoria:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontró la categoría con id: {categoria_id}"
        )
        
    # usamos la funcion buscar productos para apartir de la categoria ya seleccionada retorne suss productos
    productos = buscar_productos_por_categoria_service(categoria)
    
    # evaluamos si no retorno productos 
    if not productos or len(productos) == 0:
        raise HTTPException(
            status_code=404, 
            detail=f"La categoría '{categoria.nombre}' existe, pero no tiene productos asociados todavía."
        )
        
    return productos