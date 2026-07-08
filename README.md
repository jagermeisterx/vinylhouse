# VinylHouse 🎵

E-commerce de discos de vinilo desarrollado con Django.

## Requisitos

- Python 3.12+
- pip

## Instalación

```bash
# Clonar el repositorio
git clone <repo-url>
cd vinylhouse

# Crear y activar entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Migrar base de datos
python manage.py migrate

# Cargar datos de ejemplo (opcional)
python manage.py loaddata seed_data

# Ejecutar servidor
python manage.py runserver
```

## Rutas principales

| Ruta | Descripción | Acceso |
|------|-------------|--------|
| `/` | Catálogo de vinilos | Público |
| `/catalogo/<id>/` | Detalle del producto | Público |
| `/accounts/login/` | Iniciar sesión | Público |
| `/accounts/registro/` | Registrarse | Público |
| `/carrito/` | Carrito de compras | Cliente |
| `/carrito/confirmar/` | Confirmar compra | Cliente |
| `/ordenes/<id>/exito/` | Compra exitosa | Cliente (propietario) |
| `/mis-ordenes/` | Historial de órdenes | Cliente |
| `/mis-ordenes/<id>/` | Detalle de orden | Cliente (propietario) |
| `/admin-productos/` | Administrar productos | Admin (staff) |
| `/admin-productos/crear/` | Crear producto | Admin (staff) |
| `/admin-productos/<id>/editar/` | Editar producto | Admin (staff) |
| `/admin-productos/<id>/eliminar/` | Desactivar producto | Admin (staff) |
| `/admin/` | Django Admin nativo | Admin (staff) |

## Credenciales de prueba

| Rol | Usuario | Contraseña |
|-----|---------|------------|
| Administrador | `admin` | `admin123` |
| Cliente | `cliente` | `cliente123` |

## Estructura del proyecto

```
vinylhouse/
├── manage.py
├── requirements.txt
├── vinylhouse_project/     # Configuración del proyecto
├── accounts/               # Login, registro, logout
├── catalog/                # Productos, géneros, CRUD admin
├── cart/                   # Carrito basado en sesión
├── orders/                 # Órdenes y detalle
├── templates/              # Templates HTML
├── static/                 # Archivos estáticos (CSS)
└── media/                  # Imágenes de productos
```

## Tecnologías

- **Django 6.0** - Framework web
- **SQLite** - Base de datos
- **Bootstrap 5** - Frontend
- **Pillow** - Manejo de imágenes
