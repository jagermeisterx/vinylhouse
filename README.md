# VinylHouse 🎵

E-commerce de discos de vinilo desarrollado con Django, con integración a la API de Discogs para importar releases al catálogo.

## Características

### Para clientes
- **Catálogo público** de vinilos con portada, título, artista y precio
- **Filtro por género** musical
- **Detalle de producto** con descripción, año de lanzamiento, sello, formato y tracklist
- **Carrito de compras** basado en sesión: agregar, actualizar cantidades, quitar productos
- **Confirmación de compra** con descuento automático de stock y registro de orden
- **Historial de órdenes** con detalle completo de cada compra
- **Registro y autenticación** de usuarios

### Para administradores (staff)
- **Panel de administración de productos**: crear, editar y desactivar (soft delete)
- **Integración con Discogs API**: buscar releases en la base de datos de Discogs e importarlos al catálogo con un click
  - Importación automática de: título, artista, año, género, sello, formato, tracklist e imagen de portada
  - Anti-duplicados: no se puede importar el mismo release dos veces (campo `discogs_id` único)
  - Validaciones de stock integradas con el flujo de compra
- **Django Admin nativo** como panel de respaldo

## Roles de usuario

| Rol | Permisos |
|-----|----------|
| **Visitante** | Ver catálogo y detalle de productos (no puede comprar) |
| **Cliente** | Todo lo del visitante + carrito, compra, historial de órdenes |
| **Administrador** (`is_staff=True`) | Todo lo del cliente + panel de productos e integración Discogs |

## Requisitos

- Python 3.12+
- pip
- **Token de Discogs** (ver sección [Integración Discogs](#integración-con-discogs-api))

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

# Configurar variables de entorno
cp .env.example .env
# Editar .env y agregar tu DISCOGS_USER_TOKEN

# Migrar base de datos
python manage.py migrate

# Cargar datos de ejemplo (opcional, incluye 2 vinilos: Bowie y Pink Floyd)
python manage.py loaddata seed_data

# Crear superusuario (opcional)
python manage.py createsuperuser

# Ejecutar servidor
python manage.py runserver
```

## Rutas principales

### Públicas
| Ruta | Descripción |
|------|-------------|
| `/` | Catálogo de vinilos |
| `/catalogo/<id>/` | Detalle del producto |

### Autenticación
| Ruta | Descripción |
|------|-------------|
| `/accounts/login/` | Iniciar sesión |
| `/accounts/registro/` | Registrarse |
| `/accounts/logout/` | Cerrar sesión (POST) |

### Cliente (requiere login)
| Ruta | Descripción |
|------|-------------|
| `/carrito/` | Carrito de compras |
| `/carrito/agregar/<id>/` | Agregar producto al carrito |
| `/carrito/actualizar/<id>/` | Actualizar cantidad |
| `/carrito/quitar/<id>/` | Quitar producto del carrito |
| `/carrito/confirmar/` | Confirmar compra |
| `/ordenes/<id>/exito/` | Confirmación de compra exitosa |
| `/mis-ordenes/` | Historial de órdenes |
| `/mis-ordenes/<id>/` | Detalle de una orden |

### Administrador (requiere login + staff)
| Ruta | Descripción |
|------|-------------|
| `/admin-productos/` | Listado de productos (activos e inactivos) |
| `/admin-productos/crear/` | Crear producto manualmente |
| `/admin-productos/<id>/editar/` | Editar producto |
| `/admin-productos/<id>/eliminar/` | Desactivar producto (soft delete) |
| `/discogs/buscar/` | Buscar releases en Discogs |
| `/discogs/importar/<discogs_id>/` | Importar release de Discogs al catálogo |
| `/admin/` | Django Admin nativo |

## Credenciales de prueba

| Rol | Usuario | Contraseña |
|-----|---------|------------|
| Administrador | `admin` | `admin123` |
| Cliente | `cliente` | `cliente123` |

## Integración con Discogs API

VinylHouse se integra con la [API de Discogs](https://www.discogs.com/developers) para permitir al administrador buscar releases en la base de datos más grande de música del mundo e importarlos directamente al catálogo de la tienda.

### ¿Cómo funciona?

1. El administrador accede a `/discogs/buscar/` desde el panel de productos
2. Busca por título de álbum, artista, o ambos
3. Discogs retorna los resultados con portada, año y formato
4. El administrador hace clic en "Importar" en el release deseado
5. La app descarga automáticamente: título, artista, año, género, sello discográfico, formato, tracklist e imagen de portada
6. Se crea un `Product` en la base de datos (con `precio=0` y `stock=0`)
7. El administrador es redirigido a la edición para fijar precio y stock
8. El producto queda disponible en el catálogo público para compra

### Configuración

La integración usa **autenticación con user-token** (OAuth no es necesario para lectura). Para obtener tu token:

1. Crea una cuenta en [discogs.com](https://www.discogs.com)
2. Ve a **Settings → Developers → Generate Personal Access Token**
3. Copia el token generado
4. Crea un archivo `.env` en la raíz del proyecto (ver `.env.example`):
   ```
   DISCOGS_USER_TOKEN=tu_token_aqui
   ```

El archivo `.env` está en `.gitignore` y **nunca se commitea**.

### Validaciones

- No se puede importar el mismo release dos veces (campo `discogs_id` con `unique=True`)
- Throttling automático de 1 request/segundo (límite de la API de Discogs)
- Manejo de errores si la imagen no está disponible o la API falla

## Estructura del proyecto

```
vinylhouse/
├── manage.py
├── requirements.txt
├── .env                      # Token de Discogs (no commiteado)
├── .env.example              # Plantilla de variables de entorno
├── vinylhouse_project/       # Configuración del proyecto Django
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── accounts/                 # Autenticación: login, registro, logout
│   ├── forms.py              # LoginForm y RegisterForm (español)
│   ├── validators.py         # Validadores de contraseña en español
│   ├── views.py
│   └── urls.py
├── catalog/                  # Productos, géneros, CRUD admin, integración Discogs
│   ├── models.py             # Genre, Product (con discogs_id, sello, formato, tracklist)
│   ├── forms.py              # ProductForm
│   ├── views.py              # Catálogo público + CRUD admin + importación Discogs
│   ├── discogs_service.py    # Servicio de integración con la API de Discogs
│   ├── decorators.py         # @staff_required
│   ├── admin.py              # Configuración del Django Admin nativo
│   ├── fixtures/
│   │   └── seed_data.json    # 2 productos de ejemplo (Bowie, Pink Floyd)
│   └── urls.py
├── cart/                     # Carrito de compras (basado en sesión)
│   ├── cart.py               # Clase Cart: add, remove, update, get_total, clear
│   ├── views.py              # Vistas del carrito + confirmación de compra
│   ├── context_processors.py # Contador de ítems en el navbar
│   └── urls.py
├── orders/                   # Órdenes confirmadas
│   ├── models.py             # Order, OrderItem
│   ├── views.py              # Historial y detalle de órdenes
│   └── urls.py
├── templates/                # Templates HTML (Bootstrap 5)
│   ├── base.html             # Layout base con navbar dinámica por rol
│   ├── accounts/
│   ├── catalog/
│   ├── cart/
│   └── orders/
├── static/
│   └── css/styles.css
└── media/
    └── productos/            # Imágenes de portadas subidas/importadas
```

## Tecnologías

- **Django 6.0** — Framework web
- **SQLite** — Base de datos (desarrollo)
- **Bootstrap 5.3** — Frontend (vía CDN)
- **Pillow** — Manejo de imágenes
- **python3-discogs-client 2.8** — Cliente de la API de Discogs
- **python-dotenv** — Variables de entorno

## Datos de ejemplo

El fixture `seed_data.json` incluye dos vinilos reales como datos semilla:

| Título | Artista | Género | Año |
|--------|---------|--------|-----|
| Aladdin Sane (50th Anniversary, Silver Vinyl) | David Bowie | Glam Rock | 1973 |
| The Dark Side of the Moon (Remastered) | Pink Floyd | Rock Progresivo | 1973 |

Cargar con: `python manage.py loaddata seed_data`

## Agradecimientos

- **[Discogs](https://www.discogs.com)** — Por su excelente API pública y la base de datos de música que alimenta la integración de importación de releases en este proyecto.
- **[python3-discogs-client](https://github.com/joalla/discogs_client)** — Librería cliente de la API de Discogs mantenida por la comunidad (joalla), continuación del cliente oficial deprecado por Discogs en 2020.
- **[jesseward/discogs-oauth-example](https://github.com/jesseward/discogs-oauth-example)** — Repositorio de referencia que inspiró el enfoque de integración con la API de Discogs.
- **[Django](https://www.djangoproject.com)** — Framework web sobre el que está construido todo el proyecto.
- **[Bootstrap](https://getbootstrap.com)** — Framework CSS usado para el diseño responsivo.