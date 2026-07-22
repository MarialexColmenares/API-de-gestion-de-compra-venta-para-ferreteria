from fastapi import APIRouter, Depends, HTTPException, status
from database.conexion import engine, get_session
from sqlmodel import Session, select
from models.modelos import Categoria
from schemas.esquemas import CategoriaCreate, CategoriaRead, ProductoRead, CategoriaUpdate
from typing import List
from sqlalchemy import func

# prefix y tags para organizar las rutas de categoría en la documentación de FastAPI
router = APIRouter(prefix="/categorias", tags=["Categorías"])

#  crea una categoria nueva
@router.post("/", response_model=CategoriaRead)
def crear_categoria(data: CategoriaCreate,session: Session = Depends(get_session)):
    
    statement = select(Categoria).where(Categoria.nombre == data.nombre)
    existe = session.exec(statement).first()
    
    if existe:
        raise HTTPException(status_code=409, detail="Ya existe una categoría con este nombre")
    
    nueva_categoria = Categoria(
        nombre=data.nombre,
        estado=data.estado,
        descripcion=data.descripcion)
    
    session.add(nueva_categoria)
    session.commit()
    session.refresh(nueva_categoria)

    return nueva_categoria

#  todas las categorias
@router.get("/", response_model=List[CategoriaRead])
def obtener_categorias(session: Session = Depends(get_session)):
    
    categorias = session.exec(select(Categoria)).all()
    
    if not categorias:
        raise HTTPException(
            status_code=404,
            detail="No se encontraron categorias en la base de datos")
        
    return categorias

# mostrar categorias activas 
@router.get("/activas", response_model=List[CategoriaRead])
def categorias_activas(session: Session = Depends(get_session)):
    
    statement = select(Categoria).where(Categoria.estado == True)
    categorias = session.exec(statement).all()
    
    return categorias

# obtenemos una categoria por su id
@router.get("/{categoria_id}", response_model=CategoriaRead)
def obtener_categoria(categoria_id: int, session: Session = Depends(get_session)):
    categoria = session.get(Categoria, categoria_id)
    
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Categoría con ID {categoria_id} no encontrada")
    
    return categoria

#  eliminacion logica de categoria
@router.delete("/{categoria_id}")
def desactivar_categoria(categoria_id: int, session: Session = Depends(get_session)):
    
    categoria = session.get(Categoria, categoria_id)
    
    if not categoria:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND, 
            detail="Categoría no encontrada"
        )
    
    categoria.estado = False
    
    session.commit()
    session.refresh(categoria)
    return {"message": f"Categoría con ID {categoria_id} ha sido desactivada (estado cambiado a False)"}

#  reactivar categoria
@router.patch("/{categoria_id}/activar")
def activar_categoria(categoria_id: int, session: Session = Depends(get_session)):
    categoria = session.get(Categoria, categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    categoria.estado = True
    
    session.add(categoria)
    session.commit()
    return {"message": f"Categoría '{categoria.nombre}' activada nuevamente"}

# actualizacion parcial
@router.patch("/{categoria_id}", response_model=CategoriaRead)
def editar_categoria(categoria_id: int, data: CategoriaUpdate, session: Session = Depends(get_session)):
    
    categoria_db = session.get(Categoria, categoria_id)
    
    if not categoria_db:
        raise HTTPException(
            status_code=404, 
            detail=f"Categoría con ID {categoria_id} no encontrada")
        
    if data.nombre is not None:
        categoria_db.nombre = data.nombre
    if data.descripcion is not None:
        categoria_db.descripcion = data.descripcion

    session.add(categoria_db)
    session.commit()
    session.refresh(categoria_db)
    
    return categoria_db

# productos por categoria 
@router.get("/{nombre_categoria}/productos", response_model=List[ProductoRead])
def buscar_productos_por_categoria(nombre_categoria: str, session: Session = Depends(get_session)):
    # Convertimos el nombre en la BD y el parámetro de búsqueda a minúsculas
    statement = select(Categoria).where(func.lower(Categoria.nombre) == nombre_categoria.lower())
    categoria = session.exec(statement).first()
    
    if not categoria:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontró la categoría: {nombre_categoria}"
        )
    productos = categoria.productos
    
    # Validación B: ¿La categoría existe pero no tiene productos registrados?
    if not productos or len(productos) == 0:
        raise HTTPException(
            status_code=404, 
            detail=f"La categoría '{categoria.nombre}' existe, pero no tiene productos asociados todavía."
        )
        
    return productos