from sqlmodel import select
from models.modelos import Categoria


def crear_categoria_service(data, session):
    
    #  seleccionamos categorias con el mismo nombre
    categoria = session.exec(select(Categoria).where(Categoria.nombre == data.nombre)).first()
        
    # si ya existe una categoria retornamos None
    if categoria:
       return None 
        
    # creamos la instancia del modelo categoria
    nueva_categoria = Categoria(
        nombre=data.nombre,
        estado=data.estado,
        descripcion=data.descripcion)
        
    session.add(nueva_categoria)
    session.commit()
    session.refresh(nueva_categoria)

    # se retorna la nueva categoria 
    return nueva_categoria

def obtener_categorias_service(session):
    
    categorias = session.exec(select(Categoria)).all()

    return categorias

def categorias_activas_service(session):
    
    # seleccionamos las categorias con estado True
    categorias = session.exec(select(Categoria).where(Categoria.estado == True)).all()
    
    return categorias 

def obtener_categoria_service(categoria_id, session):
    
    categoria = session.get(Categoria, categoria_id)
    
    return categoria
    
def desactivar_categoria_service(categoria_id, session):
    
    # seleccionamos la categoria a partir del id 
    categoria = session.get(Categoria, categoria_id)
    
    # sino existe categoria retornamos None saltandonos lo que queda de la funcion
    if not categoria:
        return None 
        
    categoria.estado = False
        
    session.commit()
    session.refresh(categoria)
    
    return categoria

def activar_categoria_service(categoria_id, session):
    categoria = session.get(Categoria, categoria_id)
    
    if not categoria:
        return None
        
    categoria.estado = True
        
    session.add(categoria)
    session.commit()
    
    return categoria

def editar_categoria_service(categoria_id, data, session):
    
    categoria_db = session.get(Categoria, categoria_id)
    
    if not categoria_db:
        return None
    
    if data.nombre is not None:
        categoria_db.nombre = data.nombre
    if data.descripcion is not None:
        categoria_db.descripcion = data.descripcion
    
    session.add(categoria_db)
    session.commit()
    session.refresh(categoria_db)
    
    return categoria_db

def buscar_productos_por_categoria_service(categoria):
    
    productos = categoria.productos
    
    return productos
