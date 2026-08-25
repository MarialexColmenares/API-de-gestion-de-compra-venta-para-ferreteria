from sqlmodel import select
from models.modelos import Marca


def crear_marca_service(data, session):
    # seleccionamos marcas con el mismo nombre
    marca_existente = session.exec(select(Marca).where(Marca.nombre == data.nombre)).first()

    # si ya existe una marca retornamos None
    if marca_existente:
        return None

    # creamos la instancia del modelo marca
    nueva_marca = Marca(nombre=data.nombre, estado=data.estado)
    
    session.add(nueva_marca)
    session.commit()
    session.refresh(nueva_marca)

    return nueva_marca


def obtener_marcas_service(session):
    # seleccionamos todas las marcas de la db
    return session.exec(select(Marca)).all()


def buscar_marcas_service(nombre, session):
    # buscamos marcas cuyo nombre coincida parcialmente
    return session.exec(select(Marca).where(Marca.nombre.contains(nombre))).all()


def obtener_marca_service(marca_id, session):
    # seleccionamos la marca a partir de su id
    return session.get(Marca, marca_id)


def actualizar_marca_service(marca_id, data, session):
    marca_db = session.get(Marca, marca_id)
    if not marca_db:
        return None

    if data.nombre is not None:
        marca_db.nombre = data.nombre

    session.add(marca_db)
    session.commit()
    session.refresh(marca_db)
    return marca_db


def desactivar_marca_service(marca_id, session):
    marca_db = session.get(Marca, marca_id)
    if not marca_db:
        return None

    # no se desactiva una marca que tenga productos vinculados
    if marca_db.productos:
        return {"error": f"No se puede desactivar '{marca_db.nombre}' porque tiene {len(marca_db.productos)} productos vinculados"}

    marca_db.estado = False
    session.add(marca_db)
    session.commit()
    return marca_db


def activar_marca_service(marca_id, session):
    marca_db = session.get(Marca, marca_id)
    if not marca_db:
        return None

    marca_db.estado = True
    session.add(marca_db)
    session.commit()
    return marca_db


def obtener_estadisticas_marca_service(marca_id, session):
    marca_db = session.get(Marca, marca_id)
    if not marca_db:
        return None

    return {
        "marca": marca_db.nombre,
        # usamos len para contar los productos asociados a la marca
        "total_productos_asociados": len(marca_db.productos),
        "estado": "Activa" if marca_db.estado else "Inactiva"
    }


def productos_de_marca_service(marca_id, session):
    
    marca_db = session.get(Marca, marca_id)
    
    productos = [producto for producto in marca_db.productos if producto.estado]
    
    return productos
