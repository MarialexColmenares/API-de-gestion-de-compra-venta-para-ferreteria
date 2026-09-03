from fastapi import APIRouter, Depends, HTTPException, status
from database.conexion import get_session
from sqlmodel import Session
from schemas.esquemas import ClienteCreate, ClienteRead, ClienteUpdate, VentaRead
from typing import List
from services.clientes_services import *
from services.autenticacion import require_roles, get_current_user

router = APIRouter(prefix="/clientes", tags=["Clientes"])

# listar clientes
@router.get("/", response_model=List[ClienteRead])
def obtener_clientes(session: Session = Depends(get_session), current_user: dict = Depends(require_roles("admin"))):
    
    # usamos la funcion service para traer todos los registros de clientes
    clientes = obtener_clientes_service(session)
    
    # evaluamos si la funcion devolvio una lista de clientes 
    if not clientes:
        raise HTTPException(status_code=404,detail="No se encontraron clientes en la base de datos")
        
    return clientes

# obtener clientes activos
@router.get("/activos", response_model=List[ClienteRead])
def obtener_clientes_activos(session: Session = Depends(get_session), current_user: dict = Depends(get_current_user)):
    
    
    clientes_activos = obtener_clientes_activos_service(session)
    
    if not clientes_activos:
        raise HTTPException(status_code=404, detail="No hay clientes activos")
    
    return clientes_activos

#  obtener cliente por id
@router.get("/{id_cliente}" , response_model=ClienteRead)
def obtener_cliente_id(id_cliente: int, session: Session = Depends(get_session), current_user: dict = Depends(get_current_user)):
    
    cliente = obtener_cliente_id_service(id_cliente, session)
    
    if not cliente:
        raise HTTPException(status_code=404, detail="cliente no encontrado")
    
    return cliente

# crear cliente
@router.post("/", response_model=ClienteRead)
def crear_cliente(data: ClienteCreate, session: Session = Depends(get_session), current_user: dict = Depends(get_current_user)):
    
    nuevo_cliente = crear_cliente_service(data, session)
    
    if nuevo_cliente == None:
        raise HTTPException(status_code=409, detail="Error: Ya existe un cliente registrado con esta cédula")

    return nuevo_cliente

# actualizacion parcial 
@router.patch("/{cliente_id}", response_model=ClienteRead)
def editar_cliente(id_cliente: int,data: ClienteUpdate,session: Session = Depends(get_session), current_user: dict = Depends(require_roles("admin"))):
    
    #  usamos la funcion service obtener cliente para obtener al cliente por su id 
    cliente_db = obtener_cliente_id_service(id_cliente, session)
    
    # evaluamos existencia del cliente 
    if not cliente_db:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    cliente_editado = editar_cliente_service(id_cliente, data, session)

    return cliente_editado

# eliminacion logica (desactivar cliente)
@router.delete("/{id_cliente}")
def desactivar_cliente(id_cliente: int, session: Session = Depends(get_session), current_user: dict = Depends(require_roles("admin"))):
    
    cliente_db = obtener_cliente_id_service(id_cliente, session)
    
    if not cliente_db:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    cliente_desactivado = desactivar_cliente_service(id_cliente, session)
    

    return {"message": f"Cliente {cliente_desactivado.nombre} {cliente_desactivado.apellido} desactivado"}

# acitvar cliente (revertir desactivacion)
@router.patch("/{id_cliente}/activar")
def activar_cliente(id_cliente: int, session: Session = Depends(get_session), current_user: dict = Depends(require_roles("admin"))):
    
    cliente_db = obtener_cliente_id_service(id_cliente, session)
    
    if not cliente_db:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    cliente_activado = activar_cliente_service(id_cliente, session)
    
    return {"message": f"Cliente {cliente_activado.nombre} {cliente_activado.apellido} activado"}

# obtener cliente por cedula
@router.get("/cedula/{num_cedula}", response_model=ClienteRead)
def obtener_por_cedula(num_cedula: str, session: Session = Depends(get_session), current_user: dict = Depends(require_roles("admin", "vendedor"))):
    
    cliente = obtener_por_cedula_service(num_cedula,session)
    
    if not cliente:
        raise HTTPException(status_code=404, detail="No existe un cliente con esa cédula")
    
    return cliente

# obtener ventas relacionadas a un cliente 
@router.get("/{id_cliente}/ventas", response_model=List[VentaRead])
def obtener_ventas_cliente(id_cliente: int, session: Session = Depends(get_session), current_user: dict = Depends(require_roles("admin", "vendedor"))):
    
    cliente = obtener_cliente_id_service(id_cliente, session)
    
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    ventas = obtener_ventas_cliente_service(id_cliente, session)

    # Al retornar cliente.ventas, FastAPI usará el nuevo VentaRead 
    # y verá que ahora sí tiene el campo 'detalles'
    if not ventas:
        raise HTTPException(status_code=404, detail="No hay ventas para este cliente")
        
    return ventas

# estadisticas cliente
@router.get("/{id_cliente}/estadisticas")
def estadisticas_cliente(id_cliente: int, session: Session = Depends(get_session), current_user: dict = Depends(require_roles("admin", "vendedor"))):
    
    cliente = obtener_cliente_id_service(id_cliente, session)
    if not cliente:
        raise HTTPException(404, "Cliente no encontrado")
    
    estadisticas = estadisticas_cliente_service(id_cliente, session)
    
    return estadisticas