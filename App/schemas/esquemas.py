from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from datetime import date
from sqlmodel import Field

class UsuarioBase(BaseModel):
    username: str = Field (min_length=3, max_length=50, description="Nombre de usuario")
    rol: str = Field(default="admin", description="Rol asignado al usuario")

class UsuarioCreate(UsuarioBase):
    contrasena: str = Field (min_length=8, description="La contraseña debe tener al menos 8 caracteres")

class UsuarioRead(UsuarioBase):
    id: int
    estado: bool
    
    # ahora usamos model_config para que al hacer consultas, nos devuelva los datos de la base de datos, en lugar de un objeto ORM, antes usabamos Config, pero ahora es model_config ya que nos generaba advertencias en la consola al hacer pruebas con pytest
    model_config = ConfigDict(from_attributes=True)

# --- ESQUEMAS DE CATEGORÍA ---
class CategoriaBase(BaseModel):
    nombre: str
    estado: bool = True
    descripcion: str

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaRead(CategoriaBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
        
class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None

# --- ESQUEMAS DE MARCA ---
class MarcaBase(BaseModel):
    nombre: str
    estado: bool = True
    
class MarcaCreate(MarcaBase):
    pass

class MarcaRead(MarcaBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
        
class MarcaUpdate(BaseModel):
    nombre: Optional[str] = None

# --- ESQUEMAS DE PRODUCTO ---
class ProductoBase(BaseModel):
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    precio: float
    costo: float
    unidad: str
    estado: bool = True
    categoria_id: int
    marca_id: int

class ProductoCreate(ProductoBase):
    pass

class ProductoRead(ProductoBase):
    id: int
    stock_total: int 

    model_config = ConfigDict(from_attributes=True)

class ProductoUpdate(BaseModel):
    codigo: str
    nombre: str
    descripcion: str
    precio: float
    costo: float
    stock_total: int
    unidad: str
    estado: bool = True
    categoria_id: int
    marca_id: int

class ProductoUpdateParcial(BaseModel):
    codigo: Optional[str] = None
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio: Optional[float] = None
    costo: Optional[float] = None
    unidad: Optional[str] = None
    categoria_id: Optional[int] = None
    marca_id: Optional[int] = None

class AsignarProductoAlmacen(BaseModel):
    producto_id: int
    almacen_id: int
    cantidad: int

# --- ESQUEMAS DE PROVEEDOR ---
class ProveedorBase(BaseModel):
    nombre_empresa: str
    contacto: str
    telefono: str
    correo: str
    direccion: str
    estado: bool = True
    
class ProveedorCreate(ProveedorBase):
    pass

class ProveedorRead(ProveedorBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
        
class ProveedorUpdate(BaseModel):
    nombre_empresa: Optional [str] = None
    contacto: Optional [str] = None
    telefono: Optional [str] = None
    correo: Optional [str] = None
    direccion: Optional [str] = None
    estado: Optional [bool] = None

# --- ESQUEMAS DE CLIENTE ---
class ClienteBase(BaseModel):
    nombre: str
    apellido: str 
    cedula: str 
    telefono: Optional[str] = None
    correo: Optional[str] = None
    direccion: Optional[str] = None
    estado: bool = True

class ClienteCreate(ClienteBase):
    pass

class ClienteRead(ClienteBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class ClienteUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    cedula: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[str] = None
    direccion: Optional[str] = None

# --- ESQUEMAS DE VENTAS ---

class DetalleVentaBase(BaseModel):
    producto_id: int
    cantidad: int
    precio_unitario: float

class DetalleVentaCreate(DetalleVentaBase):
    pass

class DetalleVentaRead(DetalleVentaBase):
    id: int
    venta_id: int
    subtotal: float
    
class VentaBase(BaseModel):
    cliente_id: int
    fecha: date
    total: float
    tipo_pago: str

class VentaCreate(VentaBase):

    detalles: List[DetalleVentaCreate] 
    
class VentaUpdate(BaseModel):
    fecha: Optional[date] = None
    total: Optional[float] = None
    tipo_pago: Optional[str] = None
    
class VentaRead(VentaBase):
    id: int
    
    detalles: List[DetalleVentaRead] = []
        
# --- ESQUEMAS DE ALMACÉN ---

class AlmacenBase(BaseModel):
    nombre: str
    ubicacion: Optional[str] = None
    estado: bool = True

class AlmacenCreate(AlmacenBase):
    pass

class AlmacenRead(AlmacenBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class AlmacenUpdate(BaseModel):
    # Se usa para el PATCH, todos los campos son opcionales
    nombre: Optional[str] = None
    ubicacion: Optional[str] = None
    
# --- ESQUEMAS DE COMPRAS ---

class DetalleCompraCreate(BaseModel):
    producto_id: int
    cantidad: int
    precio_compra: float

class CompraCreate(BaseModel):
    proveedor_id: int
    almacen_id: int  
    monto_total: float
    fecha: Optional[date] = None
    estado: str = "Recibido"
    detalles: List[DetalleCompraCreate]

class DetalleCompraRead(DetalleCompraCreate):
    id: int
    compra_id: int
    subtotal: float
    
    model_config = ConfigDict(from_attributes=True)

class CompraRead(BaseModel):
    id: int
    proveedor_id: int
    monto_total: float
    fecha: date
    estado: str # Para que al consultar la compra también lo muestre
    detalles: List[DetalleCompraRead]
    
    model_config = ConfigDict(from_attributes=True)
 
class CompraUpdate(BaseModel):
    proveedor_id: Optional[int] = None
    almacen_id: Optional[int] = None
    monto_total: Optional[float] = None
    fecha: Optional[date] = None
    estado: Optional[str] = None # Ejemplo: "Pendiente", "Recibida", "Cancelada"
    
    model_config = ConfigDict(from_attributes=True)
