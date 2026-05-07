from typing import List, Optional
from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel


class Categoria(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(index=True)
    descripcion: str
    estado: bool = Field(default=True)
    # Relación inversa
    productos: List["Producto"] = Relationship(back_populates="categoria")

class Marca(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(index=True)
    estado: bool = Field(default=True)
    
    # Relación inversa
    productos: List["Producto"] = Relationship(back_populates="marca")
    
class ProductoAlmacen(SQLModel, table=True):
    producto_id: Optional[int] = Field(default=None, foreign_key="producto.id", primary_key=True)
    almacen_id: Optional[int] = Field(default=None, foreign_key="almacen.id", primary_key=True)
    cantidad: int = Field(default=0) # Stock específico en este almacén
   
class Almacen(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    ubicacion: str
    estado: bool = Field(default=True)
    
    productos: List["Producto"] = Relationship(back_populates="almacenes", link_model=ProductoAlmacen)

class Producto(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    codigo: str = Field(unique=True, index=True)
    nombre: str = Field(index=True)
    descripcion: Optional[str] = None
    precio: float
    costo: float
    stock_total: int = Field(default=0)
    unidad: str # Unidades, Metros, Kilos
    estado: bool = Field(default=True)

    categoria_id: int = Field(foreign_key="categoria.id")
    marca_id: int = Field(foreign_key="marca.id")

    # Relaciones para acceder a los datos de las llaves foráneas
    categoria: Optional[Categoria] = Relationship(back_populates="productos")
    marca: Optional[Marca] = Relationship(back_populates="productos")
    
    # Relación con almacenes a través de la tabla intermedia
    almacenes: List[Almacen] = Relationship(back_populates="productos", link_model=ProductoAlmacen)

class Proveedor(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre_empresa: str
    contacto: str
    telefono: str
    correo: str
    direccion: str
    estado: bool = Field(default=True)

    # ESTA ES LA LÍNEA QUE FALTA O ESTÁ MAL ESCRITA:
    compras: List["Compra"] = Relationship(back_populates="proveedor")

class Cliente(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    apellido: str 
    cedula: str = Field(unique=True, index=True) 
    telefono: Optional[str] = None
    correo: Optional[str] = None
    direccion: Optional[str] = None
    estado: bool = Field(default=True)

    # Relación con ventas
    ventas: List["Venta"] = Relationship(back_populates="cliente")

class Venta(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    fecha: datetime = Field(default_factory=datetime.now)
    total: float
    tipo_pago: str 
    estado: str = Field(default="Completada")
    
    cliente_id: int = Field(foreign_key="cliente.id")

    cliente: Optional["Cliente"] = Relationship(back_populates="ventas")
    
    # Agregamos 'lazy="subquery"' para forzar la carga de los detalles
    detalles: List["DetalleVenta"] = Relationship(
        back_populates="venta", 
        sa_relationship_kwargs={"lazy": "subquery"}
    )

class DetalleVenta(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    venta_id: int = Field(foreign_key="venta.id")
    producto_id: int = Field(foreign_key="producto.id")
    cantidad: int
    precio_unitario: float
    subtotal: float # Se calcula como cantidad * precio_unitario
    
    venta: Optional["Venta"] = Relationship(back_populates="detalles")
    
    producto: Optional["Producto"] = Relationship()
    
class Compra(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    fecha: datetime = Field(default_factory=datetime.now)
    monto_total: float
    estado: str = Field(default="Pendiente", nullable=False) # pendeiente
    
    proveedor_id: int = Field(foreign_key="proveedor.id")
    almacen_id: int = Field(foreign_key="almacen.id")
    # Esta línea debe coincidir con el back_populates de arriba
    proveedor: Optional[Proveedor] = Relationship(back_populates="compras")
    detalles: List["DetalleCompra"] = Relationship(back_populates="compra")

class DetalleCompra(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    compra_id: int = Field(foreign_key="compra.id")
    producto_id: int = Field(foreign_key="producto.id")
    cantidad: int
    precio_compra: float # El precio que nos dio el proveedor
    subtotal: float

    # Relaciones
    compra: Optional[Compra] = Relationship(back_populates="detalles")
    producto: Optional["Producto"] = Relationship()
    
    