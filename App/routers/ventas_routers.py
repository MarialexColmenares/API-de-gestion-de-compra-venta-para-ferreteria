from fastapi import APIRouter, Depends, HTTPException, status
from database.conexion import get_session
from sqlmodel import Session, select
from models.modelos import Venta, DetalleVenta, Producto, Cliente, ProductoAlmacen
from schemas.esquemas import VentaCreate, VentaRead
from typing import List
from datetime import date 
from sqlalchemy import func

router = APIRouter(prefix="/ventas", tags=["Ventas"])

# crear venta con validación de cliente y stock 
@router.post("/", response_model=VentaRead, status_code=status.HTTP_201_CREATED)
def crear_venta(data: VentaCreate, session: Session = Depends(get_session)):
    cliente = session.get(Cliente, data.cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    # 1. Verificar stock global primero
    # (Evitamos cálculos si de entrada no hay suficiente en total)
    for item in data.detalles:
        prod = session.get(Producto, item.producto_id)
        if not prod or prod.stock_total < item.cantidad:
            raise HTTPException(
                status_code=400, 
                detail=f"Stock global insuficiente para: {prod.nombre if prod else 'ID ' + str(item.producto_id)}"
            )

    nueva_venta = Venta(
        cliente_id=data.cliente_id,
        fecha=data.fecha,
        total=data.total,
        tipo_pago=data.tipo_pago
    )
    
    detalles_db = []

    for item in data.detalles:
        producto = session.get(Producto, item.producto_id)
        cantidad_por_descontar = item.cantidad

        # 2. BUSQUEDA AUTOMÁTICA EN ALMACENES
        # Traemos los almacenes que tienen el producto, ordenados por cantidad descendente
        statement = select(ProductoAlmacen).where(
            ProductoAlmacen.producto_id == item.producto_id,
            ProductoAlmacen.cantidad > 0
        ).order_by(ProductoAlmacen.cantidad.desc())
        
        existencias_almacen = session.exec(statement).all()

        for stock_reg in existencias_almacen:
            if cantidad_por_descontar <= 0:
                break
            
            # Determinamos cuánto podemos sacar de este almacén
            cantidad_a_sacar = min(stock_reg.cantidad, cantidad_por_descontar)
            
            # Restamos de la tabla intermedia (ProductoAlmacen)
            stock_reg.cantidad -= cantidad_a_sacar
            cantidad_por_descontar -= cantidad_a_sacar
            
            session.add(stock_reg)

        # 3. Restar del stock global en la tabla Producto
        producto.stock_total -= item.cantidad
        session.add(producto)

        # 4. Crear el detalle de la venta
        nuevo_detalle = DetalleVenta(
            venta=nueva_venta,
            producto_id=item.producto_id,
            cantidad=item.cantidad,
            precio_unitario=item.precio_unitario,
            subtotal=item.cantidad * item.precio_unitario
        )
        detalles_db.append(nuevo_detalle)

    nueva_venta.detalles = detalles_db
    session.add(nueva_venta)
    session.commit()
    session.refresh(nueva_venta)
    
    return nueva_venta

# obtener todas las ventas
@router.get("/", response_model=List[VentaRead])
def listar_ventas(session: Session = Depends(get_session)):
    
    ventas = session.exec(select(Venta)).all()
    
    return ventas

# obtener venta por id
@router.get("/ventas/{venta_id}")
def obtener_factura(venta_id: int, session: Session = Depends(get_session)):
    # 1. Buscamos la venta
    venta = session.get(Venta, venta_id)
    
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    
    # 2. TRUCO MANUAL: Forzamos a Python a leer los detalles ANTES de responder.
    # Simplemente al acceder a 'venta.detalles', SQLModel hace la consulta.
    detalles_reales = []
    for item in venta.detalles:
        detalles_reales.append({
            "producto_id": item.producto_id,
            "cantidad": item.cantidad,
            "precio_unitario": item.precio_unitario,
            "subtotal": item.subtotal
        })
    
    # 3. Construimos la respuesta con los datos que ya extrajimos
    return {
        "id_factura": venta.id,
        "fecha": venta.fecha,
        "total_venta": venta.total,
        "items": detalles_reales  # <--- Ahora esta lista ya tiene datos
    }
    
    
# actulizacion parcial
@router.patch("/{venta_id}", response_model=VentaRead)
def actualizar_venta(venta_id: int, data: VentaCreate, session: Session = Depends(get_session)):
    venta = session.get(Venta, venta_id)
    
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    
    venta.fecha = data.fecha
    venta.total = data.total
    venta.tipo_pago = data.tipo_pago
    
    session.commit()
    session.refresh(venta)
    
    return venta

@router.get("/cliente/{cliente_id}", response_model=List[VentaRead])
def obtener_ventas_por_cliente(cliente_id: int, session: Session = Depends(get_session)):
    # 1. Verificamos existencia del cliente
    cliente = session.get(Cliente, cliente_id)
    if not cliente:
        raise HTTPException(
            status_code=404, 
            detail="Cliente no encontrado")
    
    # 2. Consultamos sus ventas
    # El lazy="subquery" que pusimos antes se encarga de los detalles automáticamente
    statement = select(Venta).where(Venta.cliente_id == cliente_id)
    ventas = session.exec(statement).all()
    
    if not ventas: 
        raise HTTPException(
            status_code=404, 
            detail=f"no se encontro un historial de ventas del cliente {cliente_id}")
    
    return ventas

# obtener ventas por rango de fechas
@router.get("/fecha/", response_model=List[VentaRead])
def obtener_ventas_por_rango_fechas(
    inicio: date, 
    fin: date, 
    session: Session = Depends(get_session)):
    
    statement = select(Venta).where(
        Venta.fecha >= inicio,
        Venta.fecha <= fin)
    
    ventas = session.exec(statement).all()
    
    if not ventas: 
        raise HTTPException( status_code=404,detail=f"no hay ventas entre esas fechas" )

    return ventas

@router.patch("/{venta_id}/cancelar")
def cancelar_venta(venta_id: int, session: Session = Depends(get_session)):
    
    venta = session.get(Venta, venta_id)
    
    if not venta or venta.estado != "Completada":
        raise HTTPException(status_code=400, detail="Venta no cancelable")
    
    for detalle in venta.detalles:
        producto = session.get(Producto, detalle.producto_id)
        producto.stock_total += detalle.cantidad
    
    venta.estado = "Cancelada"
    session.commit()
    return {"message": "Venta cancelada, stock devuelto"}


@router.get("/reporte/diario")
def reporte_ventas(fecha: date, session: Session = Depends(get_session)):
    # Filtra ventas que ocurrieron en un día específico
    statement = select(Venta).where(func.date(Venta.fecha) == fecha)
    ventas = session.exec(statement).all()
    total_dia = sum(v.total for v in ventas)
    
    return {
        "fecha": fecha,
        "cantidad_ventas": len(ventas),
        "ingreso_total": total_dia
    }