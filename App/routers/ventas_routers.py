from fastapi import APIRouter, Depends, HTTPException, status
from database.conexion import get_session
from sqlmodel import Session, select
from models.modelos import Venta, Cliente
from schemas.esquemas import VentaCreate, VentaRead
from typing import List
from datetime import date 
from sqlalchemy import func
from services.ventas_services import *
from services.autenticacion import require_roles, get_current_user

router = APIRouter(prefix="/ventas", tags=["Ventas"])

# crear venta con validación de cliente y stock 
@router.post("/", response_model=VentaRead, status_code=status.HTTP_201_CREATED)
def crear_venta(data: VentaCreate, session: Session = Depends(get_session), current_user: dict = Depends(require_roles("admin", "vendedor"))):
    resultado = crear_venta_service(data, session)
    if isinstance(resultado, dict):
        raise HTTPException(status_code=400, detail=resultado["error"])
    return resultado

# obtener todas las ventas
@router.get("/", response_model=List[VentaRead])
def listar_ventas(session: Session = Depends(get_session), current_user: dict = Depends(get_current_user)):
    
    ventas = obtener_ventas_service(session)
    
    return ventas

# obtener venta por id
@router.get("/ventas/{venta_id}")
def obtener_factura(venta_id: int, session: Session = Depends(get_session), current_user: dict = Depends(require_roles("admin", "vendedor"))):
    # 1. Buscamos la venta
    venta = obtener_venta_service(venta_id, session)
    
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
def actualizar_venta(venta_id: int, data: VentaCreate, session: Session = Depends(get_session), current_user: dict = Depends(require_roles("admin", "vendedor"))):
    venta = actualizar_venta_service(venta_id, data, session)
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return venta
 

@router.get("/cliente/{cliente_id}", response_model=List[VentaRead])
def obtener_ventas_por_cliente(cliente_id: int, session: Session = Depends(get_session), current_user: dict = Depends(require_roles("admin", "vendedor"))):
    
    # 1. Verificamos existencia del cliente
    cliente = obtener_cliente_id_service(cliente_id, session)
    if not cliente:
        raise HTTPException(
            status_code=404, 
            detail="Cliente no encontrado")
    
    
    ventas = obtener_ventas_por_cliente_service(cliente_id, session)
    
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
    session: Session = Depends(get_session),
    current_user: dict = Depends(require_roles("admin", "vendedor"))):
    
    ventas = obtener_ventas_por_fecha_service(inicio, fin, session)

    
    if not ventas: 
        raise HTTPException( status_code=404,detail=f"no hay ventas entre esas fechas" )

    return ventas

@router.patch("/{venta_id}/cancelar")
def cancelar_venta(venta_id: int, session: Session = Depends(get_session), current_user: dict = Depends(require_roles("admin"))):
    
    venta = cancelar_venta_service(venta_id, session)
    
    if not venta:
        raise HTTPException(status_code=400, detail="Venta no cancelable")
    
    return {"message": "Venta cancelada, stock devuelto"}

@router.get("/reporte/diario")
def reporte_ventas(fecha: date, session: Session = Depends(get_session), current_user: dict = Depends(require_roles("admin", "vendedor"))):

    reporte = reporte_ventas_service(fecha, session)

    return reporte