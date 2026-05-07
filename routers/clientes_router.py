from fastapi import APIRouter, Depends, HTTPException, status
from database.conexion import get_session
from sqlmodel import Session, select
from models.modelos import Cliente, Venta
from schemas.esquemas import ClienteCreate, ClienteRead, ClienteUpdate, VentaRead
from typing import List
from sqlalchemy.orm import joinedload 

router = APIRouter(prefix="/clientes", tags=["Clientes"])

# listar clientes
@router.get("/", response_model=List[ClienteRead])
def obtener_clientes(session: Session = Depends(get_session)):
    
    clientes = session.exec(select(Cliente)).all()
    
    if not clientes:
        raise HTTPException(status_code=404,detail="No se encontraron clientes en la base de datos")
        
    return clientes

# obtener clientes activos
@router.get("/activos", response_model=List[ClienteRead])
def obtener_clientes_activos(session: Session = Depends(get_session)):
    
    statement = select(Cliente).where(Cliente.estado == True)
    clientes_activos = session.exec(statement).all()
    
    if not clientes_activos:
        raise HTTPException(status_code=404, detail="No hay clientes activos")
    
    return clientes_activos

#  obtener cliente por id
@router.get("/{id_cliente}" , response_model=ClienteRead)
def obtener_cliente_id(id_cliente: int, session: Session = Depends(get_session)):
    
    cliente = session.get(Cliente, id_cliente)
    
    if not cliente:
        raise HTTPException(status_code=404, detail="cliente no encontrado")
    
    return cliente

# crear cliente
@router.post("/", response_model=ClienteRead)
def crear_cliente(data: ClienteCreate,session: Session = Depends(get_session)):
    
    sstatement = select(Cliente).where(Cliente.cedula == data.cedula)
    cliente_existente = session.exec(sstatement).first()
    
    if cliente_existente:
        raise HTTPException(status_code=409, detail="Error: Ya existe un cliente registrado con esta cédula")

    nuevo_cliente = Cliente(
        nombre=data.nombre,
        apellido=data.apellido,
        cedula=data.cedula,
        telefono=data.telefono,
        correo=data.correo,
        direccion=data.direccion,
        estado=True
    )
    
    session.add(nuevo_cliente)
    session.commit()
    session.refresh(nuevo_cliente)
    
    return nuevo_cliente

# actualizacion parcial 
@router.patch("/{cliente_id}", response_model=ClienteRead)
def editar_cliente(cliente_id: int,data: ClienteUpdate,session: Session = Depends(get_session)):

    cliente_db = session.get(Cliente, cliente_id)
    
    if not cliente_db:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    if data.nombre: 
        cliente_db.nombre = data.nombre
    if data.apellido: 
        cliente_db.apellido = data.apellido
    if data.cedula: 
        cliente_db.cedula = data.cedula
    if data.telefono: 
        cliente_db.telefono = data.telefono
    if data.correo: 
        cliente_db.correo = data.correo
    if data.direccion: 
        cliente_db.direccion = data.direccion

    session.add(cliente_db)
    session.commit()
    session.refresh(cliente_db)
    
    return cliente_db

# eliminacion logica (desactivar cliente)
@router.delete("/{cliente_id}")
def desactivar_cliente(cliente_id: int, session: Session = Depends(get_session)):
    
    cliente_db = session.get(Cliente, cliente_id)
    
    if not cliente_db:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    cliente_db.estado = False  
    
    session.add(cliente_db)
    session.commit()
    session.refresh(cliente_db)
    
    return {"message": f"Cliente {cliente_db.nombre} {cliente_db.apellido} desactivado"}

# acitvar cliente (revertir desactivacion)
@router.patch("/{cliente_id}/activar")
def activar_cliente(cliente_id: int, session: Session = Depends(get_session)):
    
    cliente_db = session.get(Cliente, cliente_id)
    
    if not cliente_db:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    cliente_db.estado = True
    
    session.add(cliente_db)
    session.commit()
    session.refresh(cliente_db)
    
    return {"message": f"Cliente {cliente_db.nombre} {cliente_db.apellido} activado"}

# obtener cliente por cedula
@router.get("/cedula/{num_cedula}", response_model=ClienteRead)
def obtener_por_cedula(num_cedula: str, session: Session = Depends(get_session)):
    
    statement = select(Cliente).where(Cliente.cedula == num_cedula)
    cliente = session.exec(statement).first()
    
    if not cliente:
        raise HTTPException(status_code=404, detail="No existe un cliente con esa cédula")
    
    return cliente

# obtener ventas relacionadas a un cliente 
@router.get("/{cliente_id}/ventas", response_model=List[VentaRead])
def obtener_ventas_cliente(cliente_id: int, session: Session = Depends(get_session)):
    cliente = session.get(Cliente, cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    # Al retornar cliente.ventas, FastAPI usará el nuevo VentaRead 
    # y verá que ahora sí tiene el campo 'detalles'
    if not cliente.ventas:
        raise HTTPException(status_code=404, detail="No hay ventas para este cliente")
        
    return cliente.ventas

# estadisticas cliente
@router.get("/{cliente_id}/estadisticas")
def estadisticas_cliente(cliente_id: int, session: Session = Depends(get_session)):
    cliente = session.get(Cliente, cliente_id)
    if not cliente:
        raise HTTPException(404, "Cliente no encontrado")
    
    # Cargar ventas
    session.refresh(cliente)
    ventas = cliente.ventas
    
    # Calcular estadísticas
    total_ventas = len(ventas)
    gasto_total = sum(venta.total for venta in ventas)
    promedio_compra = gasto_total / total_ventas if total_ventas > 0 else 0
    
    # Última compra
    ultima_compra = None
    if ventas:
        ultima_compra = max(venta.fecha for venta in ventas)
    
    # Resultado en variable
    estadisticas = {
        "cliente": f"{cliente.nombre} {cliente.apellido}",
        "cedula": cliente.cedula,
        "total_ventas": total_ventas,
        "gasto_total": gasto_total,
        "promedio_compra": round(promedio_compra, 2),
        "ultima_compra": ultima_compra.isoformat() if ultima_compra else None
    }
    
    return estadisticas