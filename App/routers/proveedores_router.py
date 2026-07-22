from fastapi import APIRouter, Depends, HTTPException, status
from database.conexion import get_session
from sqlmodel import Session, select
from models.modelos import Proveedor
from schemas.esquemas import ProveedorCreate, ProveedorRead, ProveedorUpdate, CompraRead
from typing import List

router = APIRouter(prefix="/proveedores", tags=["Proveedores"])

# crear proveedor
@router.post("/", response_model=ProveedorRead)
def crear_proveedor(data: ProveedorCreate, session: Session = Depends(get_session)):
    
    if session.exec(select(Proveedor).where(Proveedor.correo == data.correo)).first():
        raise HTTPException(status_code=409, detail="Correo ya registrado")
    
    nuevo_proveedor = Proveedor(
        nombre_empresa=data.nombre_empresa,
        contacto=data.contacto,
        telefono=data.telefono,
        correo=data.correo,
        direccion=data.direccion)
    
    session.add(nuevo_proveedor)
    session.commit()
    session.refresh(nuevo_proveedor)
    
    return nuevo_proveedor

#  proveedores activos 
@router.get("/activos", response_model=List[ProveedorRead])
def proveedores_activos(session: Session = Depends(get_session)):
    
    statement = select(Proveedor).where(Proveedor.estado == True)
    proveedores = session.exec(statement).all()
    
    if not proveedores:
        raise HTTPException(
            status_code=404,
            detail="No hay Proveedores activos por el momento") 
    
    return proveedores

# obtener todos los proveedores
@router.get("/", response_model=List[ProveedorRead])
def listar_proveedores(session: Session = Depends(get_session)):
    
    statement = select(Proveedor)
    proveedores = session.exec(statement).all()
    
    if not proveedores:
        raise HTTPException(status_code=404, detail=f"Aun no hay registros de proveedores")
    
    return proveedores

# obtener por id
@router.get("/{proveedor_id}", response_model=ProveedorRead)
def obtener_proveedor(proveedor_id: int, session: Session = Depends(get_session)):
    
    proveedor = session.get(Proveedor, proveedor_id)
    
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    
    return proveedor

# actualizacion parcial
@router.patch("/{proveedor_id}", response_model=ProveedorRead)
def editar_proveedor(proveedor_id: int, data: ProveedorUpdate, session: Session = Depends(get_session)):

    proveedor_db = session.get(Proveedor, proveedor_id)
    
    if not proveedor_db:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")

    if data.nombre_empresa: 
        proveedor_db.nombre_empresa = data.nombre_empresa
    if data.contacto: 
        proveedor_db.contacto = data.contacto
    if data.telefono: 
        proveedor_db.telefono = data.telefono
    if data.correo: 
        proveedor_db.correo = data.correo
    if data.direccion: 
        proveedor_db.direccion = data.direccion

    session.add(proveedor_db)
    session.commit()
    session.refresh(proveedor_db)
    
    return proveedor_db

# eliminacion logica (desactivar proveedor)
@router.delete("/{proveedor_id}")
def eliminar_proveedor(proveedor_id: int, session: Session = Depends(get_session)):
    
    proveedor_db = session.get(Proveedor, proveedor_id)
    
    if not proveedor_db:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    
    proveedor_db.estado = False  
    
    session.add(proveedor_db)
    session.commit()
    
    return {"message": f"Proveedor {proveedor_db.nombre_empresa} desactivado"}

# activar proveedor (revertir desactivacion)
@router.patch("/activar/{proveedor_id}")
def activar_proveedor(proveedor_id: int, session: Session = Depends(get_session)):
    proveedor_db = session.get(Proveedor, proveedor_id)
    
    if not proveedor_db:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    
    proveedor_db.estado = True
    
    session.add(proveedor_db)
    session.commit()
    
    return {"message": f"Proveedor {proveedor_db.nombre_empresa} activado"}

# obtener por nombre
@router.get("/filtro/{nombre}", response_model=List[ProveedorRead])  # Ruta clara
def buscar_proveedores_por_nombre(nombre: str, session: Session = Depends(get_session)):
    
    statement = select(Proveedor).where(
        Proveedor.nombre_empresa.contains(nombre),
        Proveedor.estado == True)
    
    proveedores = session.exec(statement).all()
    
    if not proveedores:
        raise HTTPException(status_code=404, detail=f"No se encontraron proveedores: {nombre}")
    
    return proveedores

# compras d¿con un proveedor
@router.get("/{proveedor_id}/compras", response_model=List[CompraRead])
def compras_proveedor(proveedor_id: int, session: Session = Depends(get_session)):
    
    proveedor = session.get(Proveedor, proveedor_id)
    
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    
    compras = proveedor.compras
    
    if not compras:
        raise HTTPException(status_code=404, detail="No se encontraron compras a este proveedor ")
    
    return 
