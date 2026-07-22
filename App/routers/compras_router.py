from fastapi import APIRouter, Depends, HTTPException, status
from database.conexion import get_session
from sqlmodel import Session, select
from models.modelos import Compra, DetalleCompra, Producto,  Almacen, ProductoAlmacen, Proveedor
from schemas.esquemas import CompraCreate, CompraRead, CompraUpdate
from typing import List
from datetime import datetime

router = APIRouter(prefix="/compras", tags=["Compras"])

@router.post("/", response_model=CompraRead, status_code=status.HTTP_201_CREATED)
def crear_compra(data: CompraCreate, session: Session = Depends(get_session)):
    # 1. Validaciones previas
    proveedor = session.get(Proveedor, data.proveedor_id)
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
        
    almacen = session.get(Almacen, data.almacen_id)
    if not almacen:
        raise HTTPException(status_code=404, detail="Almacén no encontrado")

    # 2. Crear encabezado (Nace como Pendiente)
    nueva_compra = Compra(
        proveedor_id=data.proveedor_id,
        almacen_id=data.almacen_id, # Asegúrate de que tu modelo Compra tenga este campo
        monto_total=data.monto_total,
        fecha=data.fecha or datetime.now(),
        estado="Pendiente" 
    )
    session.add(nueva_compra)
    session.flush() # Para obtener el ID de la compra sin cerrar la transacción

    # 3. Guardar detalles sin afectar stock
    for item in data.detalles:
        producto = session.get(Producto, item.producto_id)
        if not producto:
            session.rollback()
            raise HTTPException(status_code=404, detail=f"Producto {item.producto_id} no existe")

        nuevo_detalle = DetalleCompra(
            compra_id=nueva_compra.id,
            producto_id=item.producto_id,
            cantidad=item.cantidad,
            precio_compra=item.precio_compra,
            subtotal=item.cantidad * item.precio_compra
        )
        session.add(nuevo_detalle)

    session.commit()
    session.refresh(nueva_compra)
    return nueva_compra

# obtener todas las compras
@router.get("/", response_model=List[CompraRead])
def mostrar_compras(session: Session = Depends(get_session)):
    
    compras = session.exec(select(Compra)).all()
    
    if not compras:
        raise HTTPException(status_code=404, detail="No se encontro historial de compras")
    
    return compras

# obtener por id
@router.get("/{compra_id}", response_model=CompraRead)
def obtener_compra(compra_id: int, session: Session = Depends(get_session)):
    compra = session.get(Compra, compra_id)
    
    if not compra:
        raise HTTPException(status_code=404, detail="Compra no encontrada")
    
    return compra

#  recibir en un almacen la compra
@router.patch("/recibir/{compra_id}", response_model=CompraRead)
def recibir_compra(compra_id: int, session: Session = Depends(get_session)):
    compra_db = session.get(Compra, compra_id)
    if not compra_db:
        raise HTTPException(status_code=404, detail="Compra no encontrada")
    
    if compra_db.estado == "Recibido":
        raise HTTPException(status_code=400, detail="Esta compra ya fue ingresada al inventario")

    # PROCESO: Pasar de Pendiente a Recibido y sumar stock
    for item in compra_db.detalles:
        # A. Sumar al Almacén específico
        statement = select(ProductoAlmacen).where(
            ProductoAlmacen.producto_id == item.producto_id,
            ProductoAlmacen.almacen_id == compra_db.almacen_id
        )
        relacion = session.exec(statement).first()

        if relacion:
            relacion.cantidad += item.cantidad
        else:
            nueva_relacion = ProductoAlmacen(
                producto_id=item.producto_id,
                almacen_id=compra_db.almacen_id,
                cantidad=item.cantidad
            )
            session.add(nueva_relacion)

        # B. Sumar al stock total del producto
        producto = session.get(Producto, item.producto_id)
        if producto:
            producto.stock_total += item.cantidad
            session.add(producto)

    compra_db.estado = "Recibido"
    session.add(compra_db)
    session.commit()
    session.refresh(compra_db)
    return compra_db

# actualización parcial
@router.patch("/{compra_id}", response_model=CompraRead)
def actualizar_compra(compra_id: int, data: CompraUpdate, session: Session = Depends(get_session)):
    
    compra_db = session.get(Compra, compra_id)
    if not compra_db:
        raise HTTPException(status_code=404, detail="Compra no encontrada")
    
    datos_actualizar = data.dict(exclude_unset=True) 
    for key, value in datos_actualizar.items():
        setattr(compra_db, key, value)
    
    session.add(compra_db)
    session.commit()
    session.refresh(compra_db)
    return compra_db

@router.delete("/{compra_id}", response_model=CompraRead)
def cancelar_compra(compra_id: int, session: Session = Depends(get_session)):
    
    compra_db = session.get(Compra, compra_id)
    
    if not compra_db:
        raise HTTPException(status_code=404, detail="Compra no encontrada")
    
    if compra_db.estado != "Pendiente":
        raise HTTPException(status_code=400, detail="Solo se pueden cancelar compras pendientes")
    
    compra_db.estado = "Cancelado"
    
    session.add(compra_db)
    session.commit()
    session.refresh(compra_db)
    return compra_db

# obtener compras por proveedor
@router.get("/proveedor/{proveedor_id}", response_model=List[CompraRead])
def obtener_compras_por_proveedor(proveedor_id: int, session: Session = Depends(get_session)):
    
    statement = select(Compra).where(Compra.proveedor_id == proveedor_id)
    compras = session.exec(statement).all()
    
    if not compras:
        raise HTTPException(status_code=404, detail="No se encontraron compras para este proveedor")
    
    return compras


@router.get("/reporte/fechas", response_model=List[CompraRead])
def reporte_compras(fecha_inicio: datetime, fecha_fin: datetime, session: Session = Depends(get_session)):
    
    statement = select(Compra).where(Compra.fecha >= fecha_inicio, Compra.fecha <= fecha_fin)
    
    return session.exec(statement).all()