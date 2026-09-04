from datetime import date
from sqlalchemy import func
from sqlmodel import select
from models.modelos import Venta, DetalleVenta, Producto, Cliente, ProductoAlmacen
from services.clientes_services import obtener_cliente_id_service

def crear_venta_service(data, session):
    # Validar la existencia del cliente antes de procesar la venta
    cliente = session.get(Cliente, data.cliente_id)
    if not cliente:
        return {"error": "Cliente no encontrado"}
    
    # Pre-validación de inventario: Recorre todos los ítems para asegurar 
    # que existe stock total suficiente ANTES de modificar cualquier dato
    for item in data.detalles:
        producto = session.get(Producto, item.producto_id)
        if not producto or producto.stock_total < item.cantidad:
            return {"error": f"Stock global insuficiente para: {producto.nombre if producto else 'ID ' + str(item.producto_id)}"}

    #  Instanciar la cabecera de la venta con los datos principales
    nueva_venta = Venta(cliente_id=data.cliente_id, fecha=data.fecha, total=data.total, tipo_pago=data.tipo_pago)
    
    detalles_db = []
    
    # Procesar cada producto para descontar stock e ir creando el detalle de la venta
    for item in data.detalles:
        producto = session.get(Producto, item.producto_id)
        cantidad_por_descontar = item.cantidad
        
        #  Consultar los almacenes donde hay stock (> 0), priorizando los que tienen mayor cantidad
        existencias = session.exec(
            select(ProductoAlmacen)
            .where(ProductoAlmacen.producto_id == item.producto_id, ProductoAlmacen.cantidad > 0)
            .order_by(ProductoAlmacen.cantidad.desc())
        ).all()
        
        #  Descontar las unidades de los almacenes iterando hasta cubrir la cantidad requerida
        for stock_reg in existencias:
            if cantidad_por_descontar <= 0:
                break
            # Toma lo que necesite o lo máximo disponible en ese registro/almacén
            cantidad_a_sacar = min(stock_reg.cantidad, cantidad_por_descontar)
            stock_reg.cantidad -= cantidad_a_sacar
            cantidad_por_descontar -= cantidad_a_sacar
    
            # Notifica a la sesión los cambios en el registro del almacén
            session.add(stock_reg)
    
        #  Actualizar el stock acumulado global del producto
        producto.stock_total -= item.cantidad
        session.add(producto)
    
        #  Crear la línea del detalle asociando la venta, el producto, precios y subtotal
        detalles_db.append(
            DetalleVenta(
                venta=nueva_venta, 
                producto_id=item.producto_id, 
                cantidad=item.cantidad, 
                precio_unitario=item.precio_unitario, 
                subtotal=item.cantidad * item.precio_unitario
            )
        )
    
    # Asociar la lista de detalles a la venta principal
    nueva_venta.detalles = detalles_db
    
    # Guardar en BD dentro de una única transacción y refrescar para obtener los datos persistidos (como IDs autogenerados)
    session.add(nueva_venta)
    session.commit()
    session.refresh(nueva_venta)
    
    # Retornar la entidad Venta recién creada
    return nueva_venta

def obtener_ventas_service(session):
    return session.exec(select(Venta)).all()

def obtener_venta_service(venta_id, session):
    return session.get(Venta, venta_id)

def actualizar_venta_service(venta_id, data, session):
    venta = session.get(Venta, venta_id)
    
    if not venta:
        return None
    
    for campo, valor in data.model_dump(exclude_unset=True).items():
        setattr(venta, campo, valor)
        
    session.commit()
    session.refresh(venta)
    
    return venta

def obtener_ventas_por_cliente_service(cliente_id, session):
    
    return session.exec(select(Venta).where(Venta.cliente_id == cliente_id)).all()

def obtener_ventas_por_fecha_service(inicio, fin, session):
    return session.exec(select(Venta).where(Venta.fecha >= inicio, Venta.fecha <= fin)).all()

def cancelar_venta_service(venta_id, session):
    venta = session.get(Venta, venta_id)
    
    if not venta or venta.estado != "Completada":
        return None
    
    for detalle in venta.detalles:
        
        producto = session.get(Producto, detalle.producto_id)
        
        if producto:
            
            producto.stock_total += detalle.cantidad
            session.add(producto)
            
    venta.estado = "Cancelada"
    
    session.commit()
    return venta

def reporte_ventas_service(fecha, session):
    
    ventas = session.exec(select(Venta).where(func.date(Venta.fecha) == fecha)).all()
    
    return {
        "fecha": fecha,
        "cantidad_ventas": len(ventas),
        "ingreso_total": sum(venta.total for venta in ventas)
        }
