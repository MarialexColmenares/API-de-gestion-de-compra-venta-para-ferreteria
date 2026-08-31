from fastapi import APIRouter, Depends, HTTPException, status
from database.conexion import get_session
from sqlmodel import Session
from schemas.esquemas import ProductoCreate, ProductoRead, ProductoUpdate, ProductoUpdateParcial, AsignarProductoAlmacen
from typing import List, Optional
from services.productos_services import *
from services.autenticacion import get_current_user, require_roles

router = APIRouter(prefix="/productos", tags=["Productos"])

# crear producto 
@router.post("/", response_model=ProductoRead, status_code=status.HTTP_201_CREATED)
def crear_producto(data: ProductoCreate, session: Session = Depends(get_session), current_user: dict = Depends(require_roles("admin", "gestor_stock"))):
    
    nuevo_producto = crear_producto_service(data, session)
    
    if isinstance(nuevo_producto, dict):
        raise HTTPException(
            status_code=409,
            detail=nuevo_producto["error"])
    
    if not nuevo_producto:
        raise HTTPException(status_code=404, detail="Categoría o marca no encontrada")
    
    return nuevo_producto

# # obtener todos los productos
@router.get("/", response_model=List[ProductoRead])
def obtener_productos(session: Session = Depends(get_session), current_user: dict = Depends(require_roles("admin"))):

    productos = obtener_productos_service(session)
    return productos

# obtener solo los proctos activos 
@router.get("/activos", response_model=List[ProductoRead])
def productos_activos(session: Session = Depends(get_session), current_user: dict = Depends(get_current_user)):
    
    productos = productos_activos_service(session)
    
    if not productos:
        raise HTTPException(
            status_code=404,
            detail="No hay Productos activos por el momento") 
    
    return productos

# busqueda avansada
@router.get("/filtros")
def buscar_productos(
    nombre: Optional[str] = None,
    codigo: Optional[str] = None,
    categoria_id: Optional[int] = None,
    min_precio: Optional[float] = None,
    max_precio: Optional[float] = None,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)):
    
    productos = buscar_productos_service(nombre, codigo, categoria_id, min_precio, max_precio, session)
    
    return productos

#  productos con stock bajo
@router.get("/stock-bajo", response_model=List[ProductoRead])
def productos_stock_critico(min_stock: int = 5, session: Session = Depends(get_session), current_user: dict = Depends(get_current_user)):
    
    productos = productos_stock_critico_service(min_stock, session)
    
    return productos

# obtener producto por id
@router.get("/{producto_id}", response_model=ProductoRead)
def obtener_producto(producto_id: int, session: Session = Depends(get_session), current_user: dict = Depends(get_current_user)):
    
    producto = obtener_producto_service(producto_id, session)
    
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    return producto

# actualizacion completa (PUT)
@router.put("/{producto_id}", response_model=ProductoRead)
def actualizar_producto_completo(producto_id: int, data: ProductoUpdate, session: Session = Depends(get_session), current_user: dict = Depends(require_roles("admin", "gestor_stock"))):
    
    producto_db = actualizar_producto_service(producto_id, data, session)
    if not producto_db:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    return producto_db

@router.patch("/{producto_id}", response_model=ProductoRead)
def editar_producto(producto_id: int, data: ProductoUpdateParcial, session: Session = Depends(get_session), current_user: dict = Depends(require_roles("admin", "gestor_stock"))):
    
    producto_db = editar_producto_service(producto_id, data, session)
    if not producto_db:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    return producto_db

# eliminacion logica
@router.delete("/{producto_id}")
def desactivar_producto(producto_id: int, session: Session = Depends(get_session), current_user: dict = Depends(require_roles("admin", "gestor_stock"))):
    
    producto = cambiar_estado_producto_service(producto_id, False, session)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    return {"message": f"Producto '{producto.nombre}' desactivado correctamente"}

# activar producto
@router.patch("/{producto_id}/activar")
def activar_producto(producto_id: int, session: Session = Depends(get_session), current_user: dict = Depends(require_roles("admin"))):
    producto = cambiar_estado_producto_service(producto_id, True, session)
    
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    
    return {"message": f"Producto '{producto.nombre}' Activado correctamente"}

#  agregar producto a alacen 
@router.post("/asignar-almacen")
def asignar_producto_almacen(data: AsignarProductoAlmacen,session: Session = Depends(get_session), current_user: dict = Depends(require_roles("admin", "gestor_stock"))):
    
    resultado = asignar_producto_almacen_service(data, session)
    if not resultado:
        raise HTTPException(status_code=404, detail="Producto o almacén no encontrado")
    return resultado

# obtener margen de ganancia 
@router.get("/{producto_id}/utilidad")
def utilidad_producto(producto_id: int, session: Session = Depends(get_session), current_user: dict = Depends(require_roles("admin", "vendedor"))):

    resultado = utilidad_producto_service(producto_id, session)
    if not resultado:
        raise HTTPException(404, "Producto no encontrado")
    return resultado

