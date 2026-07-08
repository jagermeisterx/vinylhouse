# PRD – VinylHouse: Tienda de Vinilos (E-commerce Final)

## Product Requirements Document

**Preparado para:** Equipo de desarrollo
**Preparado por:** Jefatura de Proyecto
**Contexto académico:** Módulo 8 – Entrega Final de Portafolio (E-commerce)
**Versión:** 1.0

---

## 1. Resumen ejecutivo

VinylHouse es la versión final de portafolio de un e-commerce de discos de vinilo, integrando todo lo desarrollado en los módulos anteriores del curso. El sitio permite a clientes explorar un catálogo de vinilos persistido en base de datos, agregar productos a un carrito, ajustar cantidades y confirmar una compra que se registra como orden asociada al usuario. El administrador cuenta con un panel propio para gestionar el catálogo (crear, editar y eliminar productos).

Este PRD usa dos vinilos reales como datos de ejemplo/semilla para poblar el catálogo durante el desarrollo y las pruebas:

- **David Bowie – Aladdin Sane** (Edición 50 Aniversario, vinilo plateado limitado)
- **Pink Floyd – The Dark Side of the Moon** (Remasterizado, vinilo 180g)

---

## 2. Objetivos del proyecto

### Objetivos académicos (obligatorios según la actividad)
- Integrar autenticación con dos roles: cliente y administrador.
- Catálogo de productos persistido y gestionado con el ORM de Django.
- Flujo completo de carrito de compras: agregar, quitar, actualizar cantidades, subtotales y total.
- Confirmación de compra que registra una orden con sus ítems, asociada al usuario autenticado.
- Navegación clara y consistente entre todas las secciones.
- Validaciones de formularios con mensajes claros de éxito/error.
- Documentación completa en README para que el proyecto sea reproducible.

### Objetivos de negocio (contexto del producto)
- Ofrecer una experiencia de compra simple y confiable para coleccionistas de vinilos.
- Permitir que el administrador mantenga el catálogo actualizado sin tocar código (CRUD completo vía interfaz web).

---

## 3. Roles de usuario

| Rol | Descripción | Permisos |
|-----|-------------|----------|
| **Visitante** | Usuario sin cuenta | Puede ver el catálogo público y el detalle de productos, pero no puede comprar ni agregar al carrito |
| **Cliente** | Usuario registrado con `is_staff=False` | Ver catálogo, ver detalle, usar carrito, confirmar compra, ver su historial de órdenes |
| **Administrador** | Usuario con `is_staff=True` | Todo lo del cliente + acceso al panel de administración de productos (crear, editar, eliminar) |

**Nota técnica:** Se utiliza el campo nativo `is_staff` del modelo `User` de Django para diferenciar administradores de clientes, evitando crear un sistema de roles paralelo. Esto simplifica la integración con `@login_required` y `@user_passes_test`.

---

## 4. Arquitectura del proyecto

### 4.1 Estructura de carpetas sugerida

```
vinylhouse/
├── manage.py
├── requirements.txt
├── README.md
├── vinylhouse_project/       # Configuración del proyecto
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── accounts/                 # Login, logout, registro (opcional), perfil
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── urls.py
├── catalog/                  # Productos, categorías/géneros, panel admin de productos
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── urls.py
├── cart/                     # Carrito de compras (basado en sesión)
│   ├── cart.py                # Clase Cart, lógica del carrito
│   ├── views.py
│   └── urls.py
├── orders/                   # Órdenes/pedidos confirmados
│   ├── models.py
│   ├── views.py
│   └── urls.py
├── templates/
│   ├── base.html
│   ├── accounts/
│   ├── catalog/
│   ├── cart/
│   └── orders/
├── static/
│   └── css/
│       └── styles.css
└── media/
    └── productos/             # Imágenes de portadas subidas
```

### 4.2 Separación de responsabilidades

- **accounts** → Autenticación: login, logout, registro.
- **catalog** → Todo lo del producto: modelo, listado, detalle, y CRUD administrado.
- **cart** → Lógica del carrito, basada en la sesión del usuario (no requiere modelo persistente).
- **orders** → Una vez confirmada la compra, se convierte el contenido del carrito en una Orden persistida en base de datos.

Esta separación evita mezclar "lo que se está viendo/vendiendo" (catalog) con "lo que ya se compró" (orders), y aísla el carrito como un componente temporal e independiente.

---

## 5. Modelos de datos (Django ORM)

### 5.1 App `catalog`

**Genre** (Género musical, para categorizar el catálogo)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| nombre | CharField(max_length=100, unique=True) | Ej: "Rock", "Glam Rock", "Progresivo" |

**Product** (El vinilo)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| titulo | CharField(max_length=150) | Ej: "Aladdin Sane" |
| artista | CharField(max_length=150) | Ej: "David Bowie" |
| descripcion | TextField | Detalle del álbum, edición, tracklist resumido |
| genero | ForeignKey → Genre (null=True, blank=True) | Género musical |
| precio | DecimalField(max_digits=10, decimal_places=2) | Precio en la moneda local |
| stock | PositiveIntegerField(default=0) | Unidades disponibles |
| imagen | ImageField(upload_to='productos/') | Portada del vinilo |
| anio_lanzamiento | PositiveIntegerField (null=True, blank=True) | Ej: 1973, 1973 (Dark Side es de 1973 también) |
| activo | BooleanField(default=True) | Permite "eliminar" un producto sin borrarlo físicamente (soft delete) |
| creado_en | DateTimeField(auto_now_add=True) | Fecha de creación del registro |
| actualizado_en | DateTimeField(auto_now=True) | Última edición |

**Validaciones a nivel de modelo/formulario:**
- `precio` debe ser mayor a 0.
- `stock` no puede ser negativo (se usa `PositiveIntegerField`, que ya lo impide a nivel de base de datos, pero se debe validar también en el formulario para dar un mensaje claro).

### 5.2 App `orders`

**Order** (La orden/pedido confirmado)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| usuario | ForeignKey → User | Cliente que realizó la compra |
| fecha_creacion | DateTimeField(auto_now_add=True) | Cuándo se confirmó la orden |
| total | DecimalField(max_digits=10, decimal_places=2) | Total pagado, calculado al momento de confirmar |
| estado | CharField con choices, default `CONFIRMADA` | `CONFIRMADA`, `CANCELADA` (para el MVP no se requieren más estados) |

**OrderItem** (Cada línea de producto dentro de una orden)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| order | ForeignKey → Order (related_name='items') | A qué orden pertenece |
| producto | ForeignKey → Product | Qué vinilo se compró |
| precio_unitario | DecimalField(max_digits=10, decimal_places=2) | Precio al momento de la compra (se guarda una copia, no se referencia el precio actual del producto, por si este cambia después) |
| cantidad | PositiveIntegerField | Cuántas unidades de ese producto |
| subtotal | DecimalField(max_digits=10, decimal_places=2) | `precio_unitario * cantidad`, calculado y guardado al confirmar |

**Por qué guardar `precio_unitario` copiado:** Si el administrador cambia el precio de un producto después de la venta, el historial de órdenes pasadas no debe verse alterado. Esto es una práctica estándar en e-commerce.

---

## 6. El carrito de compras (app `cart`)

Para el MVP se recomienda implementar el carrito **basado en la sesión de Django** (no en un modelo de base de datos), ya que es más simple y suficiente para el alcance del proyecto.

### 6.1 Estructura de datos en sesión

El carrito se guarda como un diccionario dentro de `request.session`, con esta forma:

```python
# request.session['cart']
{
    "3": {"cantidad": 2, "precio": "32.990"},   # producto_id: {cantidad, precio}
    "7": {"cantidad": 1, "precio": "28.500"}
}
```

### 6.2 Clase `Cart` (recomendada en `cart/cart.py`)

Se recomienda crear una clase reutilizable con estos métodos, para no repetir lógica en cada vista (principio DRY):

```python
class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, producto, cantidad=1):
        # Agrega o incrementa cantidad de un producto

    def remove(self, producto):
        # Elimina un producto del carrito

    def update(self, producto, cantidad):
        # Actualiza la cantidad de un producto ya existente

    def get_total(self):
        # Suma de todos los subtotales

    def __iter__(self):
        # Permite recorrer el carrito en el template mostrando cada línea con su subtotal

    def clear(self):
        # Vacía el carrito (se usa después de confirmar la orden)
```

### 6.3 Validaciones del carrito (backend)

- No se puede agregar más cantidad que el `stock` disponible del producto.
- La cantidad mínima al agregar o actualizar es 1 (no se permiten cantidades en 0 o negativas; si se quiere remover un producto se usa la acción "Quitar").
- Si un producto fue desactivado (`activo=False`) después de haber sido agregado al carrito, se debe advertir al usuario al momento de confirmar la compra y quitarlo automáticamente del carrito.

---

## 7. Flujo funcional detallado

### 7.1 Catálogo público

- Ruta: `/` o `/catalogo/` → Lista todos los productos con `activo=True`, mostrando portada, título, artista y precio.
- Filtro opcional por género (mejora deseable, no obligatoria para el MVP).
- Ruta: `/catalogo/<id>/` → Detalle del producto con descripción completa, precio, stock disponible y botón "Agregar al carrito".
- Visible para visitantes y usuarios logueados por igual. Si un visitante intenta agregar al carrito, se le redirige a login.

**Datos de ejemplo para poblar el catálogo (seed data):**

| Título | Artista | Género | Precio sugerido | Año | Descripción breve |
|--------|---------|--------|-----------------|-----|---------------------|
| Aladdin Sane (50th Anniversary, Silver Vinyl) | David Bowie | Glam Rock | $34.990 | 1973 | Edición limitada del 50 aniversario en vinilo plateado. Incluye el icónico rayo en el rostro de Bowie como portada. |
| The Dark Side of the Moon (Remastered) | Pink Floyd | Rock Progresivo | $29.990 | 1973 | Edición remasterizada en vinilo 180g. Incluye temas como "Money", "Time" y "Us and Them". |

Estos dos productos se recomiendan como datos semilla (fixtures o carga manual vía admin) para probar todo el flujo: catálogo → detalle → carrito → confirmación de compra.

### 7.2 Carrito de compras

- Ruta: `/carrito/` — **Vista protegida**, requiere login.
- Muestra una tabla con: portada pequeña, título, artista, precio unitario, cantidad (editable), subtotal por línea, y botón "Quitar".
- Total general al final de la tabla.
- Acciones disponibles:
  - **Agregar al carrito** desde el detalle del producto (`POST /carrito/agregar/<id>/`).
  - **Actualizar cantidad** desde la vista del carrito (`POST /carrito/actualizar/<id>/`).
  - **Quitar producto** (`POST /carrito/quitar/<id>/`).
  - **Confirmar compra** (`POST /carrito/confirmar/`).

### 7.3 Confirmación de compra

Al hacer clic en "Confirmar compra":

1. Se valida que el carrito no esté vacío.
2. Se valida que haya stock suficiente para cada línea del carrito (por si cambió desde que se agregó).
3. Se crea un registro `Order` asociado al `request.user`, con el total calculado.
4. Por cada línea del carrito, se crea un `OrderItem` con el precio congelado al momento de la compra.
5. Se descuenta el stock de cada `Product` según la cantidad comprada.
6. Se vacía el carrito de la sesión.
7. Se redirige a una página dedicada de **"Compra exitosa"** (`/ordenes/<id>/exito/`).
8. Esa página debe mostrar:
   - Un mensaje destacado de éxito (ej: "¡Compra exitosa! Tu orden #12 ha sido registrada.").
   - Un resumen breve de la orden: cantidad de productos y total pagado.
   - Un botón/enlace claro para **volver al catálogo** (regresar al sistema), y opcionalmente otro para ver el detalle completo de la orden en "Mis órdenes".
9. Esta página de éxito **no debe ser accesible directamente escribiendo cualquier ID en la URL** para órdenes de otros usuarios: la vista debe verificar que la orden pertenezca al `request.user` autenticado, o devolver un 404.

**Recomendación técnica:** Todo este proceso (pasos 3 a 5) debe envolverse en una transacción atómica de Django (`transaction.atomic()`) para evitar que se descuente stock sin haberse creado la orden completa, o viceversa.

### 7.4 Historial de órdenes del cliente

- Ruta: `/mis-ordenes/` — Vista protegida, lista las órdenes pasadas del usuario logueado con fecha, total y cantidad de ítems.
- Ruta: `/mis-ordenes/<id>/` — Detalle de una orden específica con cada producto comprado y su precio al momento de la compra.

### 7.5 Panel de administración de productos (solo staff)

- Ruta: `/admin-productos/` — Lista todos los productos (activos e inactivos) con opciones de editar y desactivar.
- Ruta: `/admin-productos/crear/` — Formulario para crear un nuevo producto (título, artista, descripción, género, precio, stock, imagen, año).
- Ruta: `/admin-productos/<id>/editar/` — Formulario de edición.
- Ruta: `/admin-productos/<id>/eliminar/` — Realiza soft delete (`activo=False`), no borra el registro de la base de datos para preservar el historial de órdenes que lo referencian.

**Protección:** Todas estas rutas deben verificar `request.user.is_staff` tanto ocultando el enlace en el template como bloqueando el acceso directo por URL en la vista (nunca confiar solo en ocultar el botón en el frontend).

Se recomienda además usar el **Django Admin nativo** (`/admin/`) como panel de respaldo durante el desarrollo, registrando `Product`, `Genre`, `Order` y `OrderItem`, aunque el panel de administración de productos "propio" (con templates personalizados) es el que cumple el requisito académico de "vistas y templates con contenido dinámico".

---

## 8. Vistas protegidas (resumen)

| Vista | Ruta | Protección |
|-------|------|-----------|
| Catálogo | `/catalogo/` | Pública |
| Detalle de producto | `/catalogo/<id>/` | Pública |
| Carrito | `/carrito/` | `@login_required` |
| Confirmar compra | `/carrito/confirmar/` | `@login_required` |
| Compra exitosa | `/ordenes/<id>/exito/` | `@login_required` + verificar que la orden pertenezca al usuario |
| Mis órdenes | `/mis-ordenes/` | `@login_required` |
| Panel admin de productos | `/admin-productos/` | `@login_required` + `is_staff` |
| Crear/editar/eliminar producto | `/admin-productos/...` | `@login_required` + `is_staff` |

Se recomienda crear un decorador propio reutilizable `@staff_required` en `catalog/decorators.py` para no repetir la verificación de `is_staff` en cada vista administrativa (principio DRY).

---

## 9. Templates y navegación

### 9.1 Template base (`templates/base.html`)

Debe incluir:
- Header con el nombre de la tienda ("VinylHouse").
- Navbar con Bootstrap (consistente con módulos anteriores), incluyendo:
  - Enlace a "Catálogo" (siempre visible).
  - Si el usuario **no está autenticado**: enlaces a "Iniciar sesión" y "Registrarse".
  - Si el usuario **está autenticado**: enlaces a "Carrito" (con contador de ítems), "Mis órdenes", y "Cerrar sesión".
  - Si el usuario **es staff**: enlace adicional a "Administrar productos".
- Bloque de mensajes de Django (`{% if messages %}`) para mostrar confirmaciones y errores de forma consistente en toda la app.
- Footer simple.
- Bloque `{% block content %}` para el contenido específico de cada página.

Todas las páginas (catálogo, detalle, carrito, confirmación, mis órdenes, login, registro, panel admin) deben heredar de este template con `{% extends 'base.html' %}`.

### 9.2 Mapa de navegación

```
Catálogo (home)
 ├── Detalle de producto
 │     └── Agregar al carrito
 ├── Carrito
 │     ├── Actualizar cantidad
 │     ├── Quitar producto
 │     └── Confirmar compra → Página "Compra exitosa" → Volver al catálogo
 ├── Mis órdenes
 │     └── Detalle de orden
 ├── Login / Registro / Logout
 └── [Solo admin] Administrar productos
       ├── Crear producto
       ├── Editar producto
       └── Eliminar producto (soft delete)
```

---

## 10. Validaciones y mensajes (checklist obligatorio)

| Formulario | Validaciones backend |
|-----------|----------------------|
| Registro de usuario | Nombre de usuario único, contraseñas coincidentes, validadores de seguridad nativos de Django |
| Crear/editar producto | `precio > 0`, `stock >= 0`, campos obligatorios (título, artista, precio) |
| Agregar/actualizar cantidad en carrito | `cantidad >= 1`, `cantidad <= stock disponible` |
| Confirmar compra | Carrito no vacío, stock suficiente para cada línea al momento de confirmar |

Todos los errores de validación deben mostrarse junto al campo correspondiente en el formulario (usando `{{ field.errors }}` en el template), y todas las acciones exitosas deben mostrar un mensaje de confirmación usando `django.contrib.messages` (ej: "Producto agregado al carrito", "Compra confirmada", "Producto actualizado correctamente").

---

## 11. Requisitos técnicos generales

- Proyecto debe ejecutar sin errores con `python manage.py runserver`.
- Usar entorno virtual (`venv`).
- Usar SQLite para desarrollo (por defecto, sin configuración extra).
- Usar **Pillow** como dependencia para el campo `ImageField` de los productos.
- Configurar `MEDIA_URL` y `MEDIA_ROOT` en `settings.py` para servir las portadas de los vinilos.
- Todas las rutas definidas en los `urls.py` de cada app, incluidas desde el `urls.py` principal.
- Usar Django Forms (`forms.Form` o `forms.ModelForm`) para todos los formularios.
- Frontend con Bootstrap para mantener consistencia visual con módulos anteriores.

---

## 12. Plan de trabajo sugerido (fases)

### Fase 1 – Base y autenticación
- Configurar proyecto, entorno virtual, apps (`accounts`, `catalog`, `cart`, `orders`).
- Implementar login, logout y registro.
- Crear template base con navegación dinámica según rol.

### Fase 2 – Catálogo
- Modelos `Genre` y `Product`.
- Vista de catálogo y detalle de producto (públicas).
- Cargar los dos productos de ejemplo (Bowie y Pink Floyd) como datos semilla vía Django Admin o un fixture.

### Fase 3 – Carrito
- Clase `Cart` basada en sesión.
- Vistas para agregar, quitar, actualizar cantidad.
- Template del carrito con subtotales y total.

### Fase 4 – Órdenes
- Modelos `Order` y `OrderItem`.
- Vista de confirmación de compra con transacción atómica (descuenta stock, crea orden, vacía carrito).
- Historial "Mis órdenes" y detalle de orden.

### Fase 5 – Panel de administración de productos
- Vistas CRUD para productos, protegidas por `is_staff`.
- Soft delete para no perder historial de órdenes.

### Fase 6 – Pulido y entrega
- Revisar validaciones y mensajes en todos los formularios.
- Ajustar estilos con Bootstrap para una experiencia consistente.
- Escribir el `README.md` completo.
- Tomar capturas de pantalla: catálogo/home, carrito, panel admin.
- Subir a repositorio público en GitHub.

---

## 13. Entregables finales

- [ ] Proyecto comprimido en `.zip` o repositorio público en GitHub.
- [ ] `README.md` con:
  - Enlace al repositorio público.
  - Requisitos e instalación (entorno virtual, `pip install -r requirements.txt`).
  - Cómo ejecutar en local (`migrate`, `runserver`).
  - Rutas principales documentadas: públicas (catálogo), cliente (carrito, órdenes), admin (gestión de productos).
  - Credenciales de prueba: 1 usuario ADMIN y 1 usuario CLIENTE con sus contraseñas.
  - Capturas de pantalla (opcional pero recomendado): home/catálogo, carrito, panel admin.

---

## 14. Fuera del alcance del MVP

Para mantener el proyecto enfocado en los requisitos de la rúbrica, quedan explícitamente fuera de este MVP:

- Pasarela de pago real (Webpay, Stripe, etc.) — la "compra" es simulada, solo se registra la orden.
- Envío de correos de confirmación.
- Búsqueda avanzada o filtros múltiples combinados.
- Sistema de reseñas o calificaciones de productos.
- Wishlist o favoritos.
- Cupones de descuento.
- Recuperación de contraseña por correo.
- Múltiples direcciones de envío o checkout con dirección/pago.
- Internacionalización (multi-idioma, multi-moneda).
