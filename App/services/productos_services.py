from sqlmodel import select
from models.modelos import Producto, Categoria, Marca, ProductoAlmacen, Almacen

def crear_producto_service(data, session):
    # verificamos que el codigo no este registrado
    if session.exec(select(Producto).where(Producto.codigo == data.codigo)).first():
        return {"error": "Error: Ya existe un producto con este codigo"}

    # validamos las relaciones antes de crear el producto
    categoria = session.get(Categoria, data.categoria_id)
    marca = session.get(Marca, data.marca_id)
    if not categoria or not marca:
        return None

    # creamos la instancia del modelo producto
    nuevo_producto = Producto(
        codigo=data.codigo, nombre=data.nombre, descripcion=data.descripcion,
        precio=data.precio, costo=data.costo, unidad=data.unidad,
        estado=data.estado, categoria_id=data.categoria_id, marca_id=data.marca_id
    )
    session.add(nuevo_producto)
    session.commit()
    session.refresh(nuevo_producto)
    return nuevo_producto

def obtener_productos_service(session):
    return session.exec(select(Producto)).all()

def productos_activos_service(session):
    return session.exec(select(Producto).where(Producto.estado == True)).all()

def buscar_productos_service(nombre, codigo, categoria_id, min_precio, max_precio, session):
    statement = select(Producto).where(Producto.estado == True)
    if nombre:
        statement = statement.where(Producto.nombre.contains(nombre))
    if codigo:
        statement = statement.where(Producto.codigo.contains(codigo))
    if categoria_id is not None:
        statement = statement.where(Producto.categoria_id == categoria_id)
    if min_precio is not None:
        statement = statement.where(Producto.precio >= min_precio)
    if max_precio is not None:
        statement = statement.where(Producto.precio <= max_precio)
    return session.exec(statement).all()

def productos_stock_critico_service(min_stock, session):
    return session.exec(select(Producto).where(Producto.estado == True, Producto.stock_total <= min_stock)).all()

def obtener_producto_service(producto_id, session):
    return session.get(Producto, producto_id)

def actualizar_producto_service(producto_id, data, session):
    producto_db = session.get(Producto, producto_id)
    
    if not producto_db:
        return None
    
    for campo in ("codigo", "nombre", "descripcion", "precio", "costo", "stock_total", "unidad", "estado", "categoria_id", "marca_id"):
        
        # getattr(data, campo): Extrae el valor del campo recibido en el objeto data. setattr(producto_db, campo, ...): Asigna ese nuevo valor al objeto traído de la base de datos.
        
        setattr(producto_db, campo, getattr(data, campo))
        
    session.add(producto_db)
    session.commit()
    session.refresh(producto_db)
    
    return producto_db

def editar_producto_service(producto_id, data, session):
    producto_db = session.get(Producto, producto_id)
    
    if not producto_db:
        return None
    
    for campo, valor in data.model_dump(exclude_unset=True).items():
        setattr(producto_db, campo, valor)
    
    session.add(producto_db)
    session.commit()
    session.refresh(producto_db)
    
    return producto_db

def cambiar_estado_producto_service(producto_id, estado, session):
    producto_db = session.get(Producto, producto_id)
    
    if not producto_db:
        return None
    
    producto_db.estado = estado
    
    session.add(producto_db)
    session.commit()
    
    return producto_db

def asignar_producto_almacen_service(data, session):
    
    producto = session.get(Producto, data.producto_id)
    almacen = session.get(Almacen, data.almacen_id)
    
    if not producto or not almacen:
        return None

    statement = select(ProductoAlmacen).where(
        ProductoAlmacen.producto_id == data.producto_id,
        ProductoAlmacen.almacen_id == data.almacen_id
    )
    existente = session.exec(statement).first()
    
    if existente:
        existente.cantidad = data.cantidad
        
    else:
        session.add(ProductoAlmacen(producto_id=data.producto_id, almacen_id=data.almacen_id, cantidad=data.cantidad))
        
    producto.stock_total += data.cantidad
    
    session.add(producto)
    session.commit()
    
    return {"mensaje": f"Se agregaron {data.cantidad} unidades de '{producto.nombre}' al almacén '{almacen.nombre}'"}

def utilidad_producto_service(producto_id, session):
    producto = session.get(Producto, producto_id)
    if not producto:
        return None
    utilidad = producto.precio - producto.costo
    margen = (utilidad / producto.costo) * 100 if producto.costo > 0 else 0
    return {"producto": producto.nombre, "costo": producto.costo, "precio": producto.precio, "utilidad": utilidad, "margen_%": f"{margen:.1f}%"}
