# API de Gestión para Ferretería 🛠️

Este proyecto es un sistema de backend desarrollado con **FastAPI** y **PostgreSQL** para la gestión integral de una ferretería. Permite administrar inventarios, transacciones comerciales y catálogos de productos de manera eficiente.

## 🚀 Características Principales

- **Gestión de Inventario:** Control de existencias organizado por almacenes.
- **Módulo de Compras:** Registro y seguimiento de pedidos a proveedores.
- **Módulo de Ventas:** Procesamiento de ventas a clientes finales.
- **Catálogo Detallado:** Clasificación de productos por categorías y marcas.
- **Entidades:** Gestión completa de Clientes y Proveedores.

## 🛠️ Tecnologías Utilizadas

- **Lenguaje:** [Python 3.13+](https://www.python.org/)
- **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **Base de Datos:** PostgreSQL [PostgreSQL](https://www.postgresql.org/)
- **ORM:** SQLModel (basado en SQLAlchemy y Pydantic) [SQLModel](https://sqlmodel.tiangolo.com/)
- **Servidor:** Uvicorn [Uvicorn](https://uvicorn.dev/)

## 📂 Estructura del Proyecto

```text
Ferreteria/
├── database/        # Configuración y sesión de la base de datos
├── models/          # Modelos de tablas (SQLModel)
├── routers/         # Endpoints de la API (almacén, compras, ventas, etc.)
├── schemas/         # Esquemas de validación de datos
├── main.py          # Punto de entrada de la aplicación
└── .gitignore       # Configuración de archivos excluidos
```

## ⚙️ Instalación y Configuración

- Clonar el repositorio:

```
Bash
git clone https://github.com/MarialexColmenares/API-de-gestion-de-compra-venta-para-ferreteria
cd Ferreteria
```

- Configurar el entorno virtual:

```
Bash
python -m venv env
source env/Scripts/activate  # En Windows use: env\\Scripts\\activate
```

- Instalar dependencias:

```
Bash
pip install -r requeriments.txt
```

- Ejecutar el servidor de desarrollo:

```
Bash
uvicorn main:app --reload
```

## 📖 Documentación de la API

Una vez iniciado el servidor, puedes interactuar con la API a través de:

- Swagger UI: http://127.0.0.1:8000/docs

- Redoc: http://127.0.0.1:8000/redoc
