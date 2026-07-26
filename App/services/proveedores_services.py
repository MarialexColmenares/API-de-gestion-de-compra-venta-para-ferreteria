from sqlmodel import select
from models.modelos import Proveedor


def crear_proveedor_service(data, session):
    # validamos que el correo no este registrado
    if session.exec(select(Proveedor).where(Proveedor.correo == data.correo)).first():
        return None
    nuevo_proveedor = Proveedor(**data.model_dump())
    session.add(nuevo_proveedor)
    session.commit()
    session.refresh(nuevo_proveedor)
    return nuevo_proveedor


def proveedores_activos_service(session):
    return session.exec(select(Proveedor).where(Proveedor.estado == True)).all()


def obtener_proveedores_service(session):
    return session.exec(select(Proveedor)).all()


def obtener_proveedor_service(proveedor_id, session):
    return session.get(Proveedor, proveedor_id)


def editar_proveedor_service(proveedor_id, data, session):
    proveedor_db = session.get(Proveedor, proveedor_id)
    if not proveedor_db:
        return None
    for campo, valor in data.model_dump(exclude_unset=True).items():
        setattr(proveedor_db, campo, valor)
    session.add(proveedor_db)
    session.commit()
    session.refresh(proveedor_db)
    return proveedor_db


def cambiar_estado_proveedor_service(proveedor_id, estado, session):
    proveedor_db = session.get(Proveedor, proveedor_id)
    if not proveedor_db:
        return None
    proveedor_db.estado = estado
    session.add(proveedor_db)
    session.commit()
    return proveedor_db


def buscar_proveedores_service(nombre, session):
    return session.exec(select(Proveedor).where(Proveedor.nombre_empresa.contains(nombre), Proveedor.estado == True)).all()


def compras_proveedor_service(proveedor_id, session):
    proveedor = session.get(Proveedor, proveedor_id)
    if not proveedor:
        return None, None
    return proveedor, proveedor.compras
