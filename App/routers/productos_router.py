from fastapi import APIRouter, Depends, HTTPException, status
from database.conexion import engine, get_session
from sqlmodel import Session, select
from models.modelos import Producto, Categoria, Marca, ProductoAlmacen, Almacen
from schemas.esquemas import ProductoCreate, ProductoRead, ProductoUpdate, ProductoUpdateParcial, AsignarProductoAlmacen
from typing import List, Optional


router = APIRouter(prefix="/productos", tags=["Productos"])

# crear producto 
@router.post("/", response_model=ProductoRead, status_code=status.HTTP_201_CREATED)
def crear_producto(data: ProductoCreate, session: Session = Depends(get_session)):
    
    statement = select(Producto).where(Producto.codigo == data.codigo)
    codigo_producto = session.exec(statement).first()
    
    if codigo_producto:
        raise HTTPException(
            status_code=409,
            detail="Error: Ya existe un producto con este codigo")
    
    categoria = session.get(Categoria, data.categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    marca = session.get(Marca, data.marca_id)
    if not marca:
        raise HTTPException(status_code=404, detail="Marca no encontrada")

    nuevo_producto = Producto(
        codigo=data.codigo,
        nombre=data.nombre,
        descripcion=data.descripcion,
        precio=data.precio,
        costo=data.costo,
        unidad=data.unidad,
        estado=data.estado,
        categoria_id=data.categoria_id,
        marca_id=data.marca_id)
    
    session.add(nuevo_producto)
    session.commit()
    session.refresh(nuevo_producto)
    
    return nuevo_producto

# # obtener todos los productos
@router.get("/", response_model=List[ProductoRead])
def obtener_productos(session: Session = Depends(get_session)):

    productos = session.exec(select(Producto)).all()
    return productos

# obtener solo los proctos activos 
@router.get("/activos", response_model=List[ProductoRead])
def productos_activos(session: Session = Depends(get_session)):
    
    statement = select(Producto).where(Producto.estado == True)
    productos = session.exec(statement).all()
    
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
    session: Session = Depends(get_session)):
    
    statement = select(Producto).where(
        Producto.estado == True)
    
    if nombre:
        statement = statement.where(Producto.nombre.contains(nombre))
    if codigo:
        statement = statement.where(Producto.codigo.contains(codigo))
    if categoria_id:
        statement = statement.where(Producto.categoria_id == categoria_id)
    if min_precio:
        statement = statement.where(Producto.precio >= min_precio)
    if max_precio:
        statement = statement.where(Producto.precio <= max_precio)
        
    productos = session.exec(statement).all()
    
    return productos

#  productos con stock bajo
@router.get("/stock-bajo", response_model=List[ProductoRead])
def productos_stock_critico(min_stock: int = 5, session: Session = Depends(get_session)):
    
    statement = select(Producto).where(
        Producto.estado == True,
        Producto.stock_total <= min_stock)
    productos = session.exec(statement).all()
    
    return productos

# obtener producto por id
@router.get("/{producto_id}", response_model=ProductoRead)
def obtener_producto(producto_id: int, session: Session = Depends(get_session)):
    
    producto = session.get(Producto, producto_id)
    
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    return producto

# actualizacion completa (PUT)
@router.put("/{producto_id}", response_model=ProductoRead)
def actualizar_producto_completo(producto_id: int, data: ProductoUpdate, session: Session = Depends(get_session)):
    
    producto_db = session.get(Producto, producto_id)

    if not producto_db:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    producto_db.codigo = data.codigo
    producto_db.nombre = data.nombre
    producto_db.descripcion = data.descripcion
    producto_db.precio = data.precio
    producto_db.costo = data.costo
    producto_db.stock_total = data.stock_total
    producto_db.unidad = data.unidad
    producto_db.estado = data.estado
    producto_db.categoria_id = data.categoria_id
    producto_db.marca_id = data.marca_id

    session.add(producto_db)
    session.commit()
    session.refresh(producto_db)
    
    return producto_db

@router.patch("/{producto_id}", response_model=ProductoRead)
def editar_producto(producto_id: int, data: ProductoUpdateParcial, session: Session = Depends(get_session)):
    
    producto_db = session.get(Producto, producto_id)
    
    if not producto_db:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    if data.codigo: 
        producto_db.codigo = data.codigo
    if data.nombre: 
        producto_db.nombre = data.nombre
    if data.descripcion: 
        producto_db.descripcion = data.descripcion
    if data.precio is not None: 
        producto_db.precio = data.precio
    if data.costo is not None:
        producto_db.costo = data.costo
    if data.stock_total is not None:
        producto_db.stock_total = data.stock_total
    if data.unidad: 
        producto_db.unidad = data.unidad
    if data.categoria_id: 
        producto_db.categoria_id = data.categoria_id
    if data.marca_id: 
        producto_db.marca_id = data.marca_id

    session.add(producto_db)
    session.commit()
    session.refresh(producto_db)
    
    return producto_db

# eliminacion logica
@router.delete("/{producto_id}")
def desactivar_producto(producto_id: int, session: Session = Depends(get_session)):
    
    producto = session.get(Producto, producto_id)
    
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    producto.estado = False
    
    session.add(producto)
    session.commit()
    
    return {"message": f"Producto '{producto.nombre}' desactivado correctamente"}

# activar producto
@router.patch("/{producto_id}/activar")
def activar_producto(producto_id: int, session: Session = Depends(get_session)):
    producto = session.get(Producto, producto_id)
    
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    producto.estado = True
    
    session.add(producto)
    session.commit()
    
    return {"message": f"Producto '{producto.nombre}' Activado correctamente"}

#  agregar producto a alacen 
@router.post("/asignar-almacen")
def asignar_producto_almacen(data: AsignarProductoAlmacen,session: Session = Depends(get_session)):
    
    producto = session.get(Producto, data.producto_id)
    almacen = session.get(Almacen, data.almacen_id)
    
    if not producto or not almacen:
        raise HTTPException(status_code=404, detail="Producto o almacén no encontrado")
    
    statement = select(ProductoAlmacen).where(
        ProductoAlmacen.producto_id == data.producto_id,
        ProductoAlmacen.almacen_id == data.almacen_id)
    existente = session.exec(statement).first()

    
    if existente:
        existente.cantidad = data.cantidad
    else:
        nuevo_stock = ProductoAlmacen(
            producto_id=data.producto_id,
            almacen_id=data.almacen_id,
            cantidad=data.cantidad
        )
        session.add(nuevo_stock)
    
    producto.stock_total += data.cantidad
    session.add(producto)
    
    session.commit()
    return {"mensaje": f"Se agregaron {data.cantidad} unidades de '{producto.nombre}' al almacén '{almacen.nombre}'"}

# obtener margen de ganancia 
@router.get("/{producto_id}/utilidad")
def utilidad_producto(producto_id: int, session: Session = Depends(get_session)):

    producto = session.get(Producto, producto_id)
    if not producto:
        raise HTTPException(404, "Producto no encontrado")
    
    utilidad = producto.precio - producto.costo
    margen = (utilidad / producto.costo) * 100 if producto.costo > 0 else 0
    
    return {
        "producto": producto.nombre,
        "costo": producto.costo,
        "precio": producto.precio,
        "utilidad": utilidad,
        "margen_%": f"{margen:.1f}%"
    }

