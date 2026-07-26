from models.modelos import Cliente
from sqlmodel import select

def obtener_clientes_service(session):
    clientes = session.exec(select(Cliente)).all()
    
    return clientes

def obtener_clientes_activos_service(session):
    
    statement = select(Cliente).where(Cliente.estado == True)
    clientes_activos = session.exec(statement).all()
    
    return clientes_activos

def obtener_cliente_id_service(id_cliente, session):
    
    cliente = session.get(Cliente, id_cliente)
    
    return cliente

def crear_cliente_service(data, session):
    
    # evaluamos si yta existe un cliente con la cedula proporcionada en data
    sstatement = select(Cliente).where(Cliente.cedula == data.cedula)
    cliente_existente = session.exec(sstatement).first()
    
    # retornamos None si yta existeun cliente con esos datos, y manejamos la exception en el router
    if cliente_existente:
        return None
    
    # creamos la instancia del modelo para el nuevo cliente 
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
        

def editar_cliente_service(id_cliente, data, session):
    
    #  ya habiendo evaluado en el router que el cliente existe lo seleccionamos aqui para actualizarlo
    cliente_db = session.get(Cliente, id_cliente)
    
    # los campos en data se actualizan
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
    

def desactivar_cliente_service(id_cliente, session):
    
    cliente_db = session.get(Cliente, id_cliente )
    
    cliente_db.estado = False  
    
    session.add(cliente_db)
    session.commit()
    session.refresh(cliente_db)
    
    return cliente_db
     


def activar_cliente_service(id_cliente, session):
    
    cliente_db = session.get(Cliente, id_cliente)
    
    cliente_db.estado = True
        
    session.add(cliente_db)
    session.commit()
    session.refresh(cliente_db)

    return cliente_db

def obtener_por_cedula_service(num_cedula, session):
    statement = select(Cliente).where(Cliente.cedula == num_cedula)
    cliente = session.exec(statement).first()

    return cliente

def obtener_ventas_cliente_service(cliente_id, session):
    cliente = session.get(Cliente, cliente_id)
    
    # agrupamos las ventas del cliente 
    ventas = cliente.ventas
    
    return ventas

def estadisticas_cliente_service(id_cliente, session):
    
    cliente = session.get(Cliente, id_cliente)
        
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
