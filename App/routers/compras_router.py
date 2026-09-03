from fastapi import APIRouter, Depends, HTTPException, status
from database.conexion import get_session
from sqlmodel import Session, select
from models.modelos import Compra
from schemas.esquemas import CompraCreate, CompraRead, CompraUpdate
from typing import List
from datetime import datetime
from services.compras_services import *
from services.autenticacion import require_roles

router = APIRouter(prefix="/compras", tags=["Compras"])

@router.post("/", response_model=CompraRead, status_code=status.HTTP_201_CREATED)
def crear_compra(data: CompraCreate, session: Session = Depends(get_session), current_user: dict = Depends(require_roles("admin", "gestor_stock"))):
    
    resultado = crear_compra_service(data, session)
    
    if resultado is None:
        raise HTTPException(status_code=404, detail="Proveedor o almacén no encontrado")
    
    if isinstance(resultado, dict):
        raise HTTPException(status_code=404, detail=resultado["error"])
    
    return resultado

# obtener todas las compras
@router.get("/", response_model=List[CompraRead])
def mostrar_compras(session: Session = Depends(get_session), current_user: dict = Depends(require_roles("admin", "gestor_stock"))):
    
    compras = obtener_compras_service(session)
    
    if not compras:
        raise HTTPException(status_code=404, detail="No se encontro historial de compras")
    
    return compras

# obtener por id
@router.get("/{compra_id}", response_model=CompraRead)
def obtener_compra(compra_id: int, session: Session = Depends(get_session), current_user: dict = Depends(require_roles("admin", "gestor_stock"))):
    compra = obtener_compra_service(compra_id, session)
    
    if not compra:
        raise HTTPException(status_code=404, detail="Compra no encontrada")
    
    return compra

#  recibir en un almacen la compra
@router.patch("/recibir/{compra_id}", response_model=CompraRead)
def recibir_compra(compra_id: int, session: Session = Depends(get_session), current_user: dict = Depends(require_roles("admin", "gestor_stock"))):
    compra_db = recibir_compra_service(compra_id, session)
    if not compra_db:
        raise HTTPException(status_code=404, detail="Compra no encontrada o ya fue recibida")
    return compra_db

# actualización parcial
@router.patch("/{compra_id}", response_model=CompraRead)
def actualizar_compra(compra_id: int, data: CompraUpdate, session: Session = Depends(get_session), current_user: dict = Depends(require_roles("admin", "gestor_stock"))):

    compra_db = actualizar_compra_service(compra_id, data, session)
    
    if compra_db == None:
        raise HTTPException(status_code=404, detail="Compra no encontrada")
    
    return compra_db

@router.delete("/{compra_id}", response_model=CompraRead)
def cancelar_compra(compra_id: int, session: Session = Depends(get_session), current_user: dict = Depends(require_roles("admin", "gestor_stock"))):
    compra_db = cancelar_compra_service(compra_id, session)
    if not compra_db:
        raise HTTPException(status_code=400, detail="Solo se pueden cancelar compras pendientes")
    return compra_db

# obtener compras por proveedor
@router.get("/proveedor/{proveedor_id}", response_model=List[CompraRead])
def obtener_compras_por_proveedor(proveedor_id: int, session: Session = Depends(get_session), current_user: dict = Depends(require_roles("admin", "gestor_stock"))):
    
    compras = obtener_compras_proveedor_service(proveedor_id, session)
    
    if compras == None:
        raise HTTPException(status_code=404, detail="No se encontro ese proveedor")
    if not compras:
        raise HTTPException(status_code=404, detail="No se encontraron compras para este proveedor")
        
    
    return compras

@router.get("/reporte/fechas", response_model=List[CompraRead])
def reporte_compras(fecha_inicio: datetime, fecha_fin: datetime, session: Session = Depends(get_session), current_user: dict = Depends(require_roles("admin", "gestor_stock"))):
    
    compras = reporte_compras_service(fecha_inicio, fecha_fin, session)
    
    if not compras:
        raise HTTPException(status_code=404, detail="No se encontraron compras")
    
    return compras

