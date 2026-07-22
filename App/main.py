from fastapi import FastAPI
from sqlmodel import SQLModel
from database.conexion import create_db_and_tables, engine
from models.modelos import Categoria, Marca, Almacen, Producto, Proveedor, Cliente
from routers.categoria_router import router as categoria_router
from routers.marcas_router import router as marca_router
from routers.almacen_router import router as almacen_router
from routers.productos_router import router as productos_router
from routers.proveedores_router import router as proveedores_router
from routers.clientes_router import router as clientes_router
from routers.ventas_routers import router as ventas_router
from routers.compras_router import router as compras_router

app = FastAPI(
    title="Centro de Repuestos y Ferretería",
    version="1.5.0"
)

@app.get("/")
async def root():
    return {"Bienvenidos": "Sistema de Centro de Repuestos y Ferretería"}

@app.on_event("startup")
def on_startup():
   create_db_and_tables()


app.include_router(categoria_router)
app.include_router(marca_router)
app.include_router(almacen_router)
app.include_router(productos_router)
app.include_router(proveedores_router)
app.include_router(clientes_router)
app.include_router(compras_router)
app.include_router(ventas_router)


