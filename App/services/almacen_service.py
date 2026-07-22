from sqlmodel import func, select
from models.modelos import Almacen, Producto, ProductoAlmacen

def crear_almacen_service(data, session):
    
    # func.lower búsqueda insensible a mayúsculas y minúsculas
    statement = select(Almacen).where(func.lower(Almacen.nombre) == data.nombre.lower())
    almacen_existente = session.exec(statement).first()
        
    # evaluamos si ya existe un almacen y devolvemos error  
    if almacen_existente:
        return None
    
    # instanciamos el modelo almacen para un nuevo registro 
    nuevo_almacen = Almacen(
        nombre=data.nombre,
        ubicacion=data.ubicacion,
        estado=data.estado
    )
    
    session.add(nuevo_almacen)
    session.commit()
    session.refresh(nuevo_almacen)
        
    return nuevo_almacen

def obtener_almacenes_service(session):
    
    # seleccionamos almacenes en la db 
    almacenes = session.exec(select(Almacen)).all()
 
    return almacenes

def almacenes_activas_service(session):
    
    # seleccionamos los almacenes con estado == True
    statement = select(Almacen).where(Almacen.estado == True)
    almacenes = session.exec(statement).all()

    return almacenes

def buscar_almacenes_service(session, nombre, ubicacion, estado):
    
    statement = select(Almacen)
    
    # evaluamos con cual de los filtros enviados coinciden 
    if nombre:
        statement = statement.where(Almacen.nombre.contains(nombre))
    if ubicacion:
        statement = statement.where( Almacen.ubicacion.contains(ubicacion))
    if estado:
        statement = statement.where(Almacen.estado == estado)
    
    #  seleccionamos y retornamos todas las coincidencias 
    almacenes = session.exec(statement).all()
    
    return almacenes

def obtener_almacen_service(almacen_id, session):
    
    # seleccionamos el almacen apartir de su id
    almacen = session.get(Almacen, almacen_id)
    
    # retornamos None porque no existe el almacen 
    if not almacen: 
        return None
    
    return almacen    

def desactivar_almacen_service(almacen_id, session):
    
    almacen = session.get(Almacen, almacen_id)
    
    if not almacen:
        return None
    
    # para la eliminacion logica solo cambiamos el estado de Truu a False
    almacen.estado = False
    
    session.add(almacen)
    session.commit()
    
    return almacen
    
def activar_almacen_service(almacen_id, session):
    
    almacen = session.get(Almacen, almacen_id )
    
    if not almacen:
        return None
    
    # se activa el almacen cambiando su estado
    almacen.estado = True
        
    session.add(almacen)
    session.commit()
    
    return almacen


def actualizar_parcial_almacen_service(almacen_id, data, session):
    
    almacen_db = session.get(Almacen, almacen_id)
    
    if not almacen_db:
        return None
    
    if data.nombre is not None:
        almacen_db.nombre = data.nombre
    if data.ubicacion is not None:
        almacen_db.ubicacion = data.ubicacion
    
    session.add(almacen_db)
    session.commit()
    session.refresh(almacen_db)
        
    return almacen_db

def asignar_producto_a_almacen_service(data, session):
    
     # Validar que existan ambos
    producto = session.get(Producto, data.producto_id)
    almacen = session.get(Almacen, data.almacen_id)
        
    if not producto or not almacen:
        return None
    
    # Verificar si ya existe el producto en ese almacén
    statement = select(ProductoAlmacen).where(ProductoAlmacen.producto_id == data.producto_id,ProductoAlmacen.almacen_id == data.almacen_id)
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
    
    # Actualizar el stock total global del producto
    producto.stock_total += data.cantidad
    session.add(producto)
    session.commit()
        
    return {"mensaje": f"Se agregaron {data.cantidad} unidades de '{producto.nombre}' al almacén '{almacen.nombre}'"}

def ver_inventario_almacen_service(almacen):

    # seleccionamos los productos del almacen
    productos = almacen.productos
    
    # devolvemos una lista vacia sino hay productos
    if not productos:
        return []
    
    return productos