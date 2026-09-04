from datetime import datetime
from sqlmodel import select
from models.modelos import Compra, DetalleCompra, Producto, Almacen, ProductoAlmacen, Proveedor

def crear_compra_service(data, session):
    
    # validamos proveedor y almacen antes de crear la compra
    if not session.get(Proveedor, data.proveedor_id) or not session.get(Almacen, data.almacen_id):
        return None
    
    nueva_compra = Compra(proveedor_id=data.proveedor_id, 
                          almacen_id=data.almacen_id, 
                          monto_total=data.monto_total, 
                          fecha=data.fecha or datetime.now(), estado="Pendiente")
    
    session.add(nueva_compra)
    session.flush()
    
    for item in data.detalles:
        if not session.get(Producto, item.producto_id):
    
            session.rollback()
            return {"error": f"Producto {item.producto_id} no existe"}
    
        session.add(DetalleCompra(compra_id=nueva_compra.id, producto_id=item.producto_id, cantidad=item.cantidad, precio_compra=item.precio_compra, subtotal=item.cantidad * item.precio_compra))
    
    session.commit()
    session.refresh(nueva_compra)
    return nueva_compra

def obtener_compras_service(session):
    return session.exec(select(Compra)).all()

def obtener_compra_service(compra_id, session):
    return session.get(Compra, compra_id)

def recibir_compra_service(compra_id, session):
    compra = session.get(Compra, compra_id)
    
    if not compra or compra.estado == "Recibido":
        return None
    
    for item in compra.detalles:
        relacion = session.exec(select(ProductoAlmacen).where(ProductoAlmacen.producto_id == item.producto_id, ProductoAlmacen.almacen_id == compra.almacen_id)).first()
        
        if relacion:
            relacion.cantidad += item.cantidad
            
        else:
            session.add(ProductoAlmacen(producto_id=item.producto_id, almacen_id=compra.almacen_id, cantidad=item.cantidad))
        producto = session.get(Producto, item.producto_id)
        
        if producto:
            producto.stock_total += item.cantidad
            session.add(producto)
            
    compra.estado = "Recibido"
    
    session.add(compra)
    session.commit()
    session.refresh(compra)
    
    return compra

def actualizar_compra_service(compra_id, data, session):
    
    compra = session.get(Compra, compra_id)
    if not compra:
        return None
    
    for campo, valor in data.model_dump(exclude_unset=True).items():
        setattr(compra, campo, valor)
        
    session.add(compra)
    session.commit()
    session.refresh(compra)
    
    return compra

def cancelar_compra_service(compra_id, session):
    
    compra = session.get(Compra, compra_id)
    
    if not compra or compra.estado != "Pendiente":
        return None
    
    compra.estado = "Cancelado"
    
    session.add(compra)
    session.commit()
    session.refresh(compra)
    
    return compra

def obtener_compras_proveedor_service(proveedor_id, session):
    
    proveedor = session.get(Proveedor, proveedor_id)
    if not proveedor:
        return None
    
    statement = select(Compra).where(Compra.proveedor_id == proveedor_id)
    compras = session.exec(statement).all()
    
    return compras

def reporte_compras_service(fecha_inicio, fecha_fin, session):

    compras = session.exec(select(Compra).where(Compra.fecha >= fecha_inicio, Compra.fecha <= fecha_fin)).all()
    
    return compras 

