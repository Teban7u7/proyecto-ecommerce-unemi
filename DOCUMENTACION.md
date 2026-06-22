# NightDrop Licorería — Documentación del Proyecto

## Plataforma de Comercio Electrónico con Integración de Pagos Nuvei/Paymentez

---

## Tabla de Contenidos

1. [Descripción General](#descripción-general)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Estructura del Proyecto](#estructura-del-proyecto)
4. [Requisitos Previos](#requisitos-previos)
5. [Instalación y Configuración](#instalación-y-configuración)
6. [Ejecución del Proyecto](#ejecución-del-proyecto)
7. [Módulos del Backend (Django)](#módulos-del-backend-django)
8. [Servicio de Pagos (Node.js)](#servicio-de-pagos-nodejs)
9. [Frontend (React + Vite)](#frontend-react--vite)
10. [Panel de Administración (Django Admin)](#panel-de-administración-django-admin)
11. [API REST — Endpoints](#api-rest--endpoints)
12. [Flujo de Pago Nuvei](#flujo-de-pago-nuvei)
13. [Docker Compose](#docker-compose)
14. [Credenciales por Defecto](#credenciales-por-defecto)

---

## Descripción General

**NightDrop Licorería** es una plataforma de comercio electrónico diseñada como proyecto de titulación. Permite la venta en línea de productos de licorería con integración de pagos a través de **Nuvei/Paymentez Ecuador**.

### Características principales:
- **Catálogo de Productos**: 7 categorías con 14 productos precargados con imágenes
- **Carrito de Compras**: Agregar, modificar cantidades y eliminar productos
- **Pasarela de Pago Nuvei**: Soporte para Link to Pay (QR + enlace) y Checkout Modal (tarjeta)
- **Panel de Administración**: Gestión completa de productos, categorías, stock, órdenes y configuración
- **Impuestos Ecuador**: Cálculo automático de IVA (0%, 8% o 15%)
- **Microservicios**: Arquitectura basada en 3 servicios independientes

---

## Arquitectura del Sistema

La plataforma está compuesta por **3 servicios** que se comunican entre sí:

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USUARIO (Navegador)                         │
│                     http://localhost:5173                           │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   FRONTEND (React+Vite)  │
                    │      Puerto: 5173        │
                    │                          │
                    │  - Catálogo de productos │
                    │  - Carrito de compras    │
                    │  - Formulario de pago    │
                    └────────────┬─────────────┘
                                 │ Proxy /api → :8000
                                 │ Proxy /media → :8000
                    ┌────────────▼────────────┐
                    │   BACKEND (Django REST)   │
                    │      Puerto: 8000         │
                    │                           │
                    │  - API REST              │
                    │  - Panel Admin           │
                    │  - Gestión de Órdenes    │
                    │  - Autenticación JWT     │
                    └────────────┬──────────────┘
                                 │ HTTP interno
                    ┌────────────▼────────────┐
                    │  PAYMENT SERVICE (Node)   │
                    │      Puerto: 3001         │
                    │                           │
                    │  - Link to Pay API       │
                    │  - Checkout Reference    │
                    │  - Webhook receiver      │
                    │  - Autenticación Nuvei   │
                    └───────────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   NUVEI / PAYMENTEZ API   │
                    │   (Externo — Staging)      │
                    │                           │
                    │  ccapi-stg.paymentez.com  │
                    │  noccapi-stg.paymentez.com│
                    └───────────────────────────┘
```

---

## Estructura del Proyecto

```
proyecto-titulacion/
├── backend/                          # Servicio 1: Django REST Framework
│   ├── apps/
│   │   ├── accounts/                 # Autenticación y usuarios
│   │   │   ├── models.py             # CustomUser (admin/staff roles)
│   │   │   ├── views.py              # Register, Login, Profile
│   │   │   ├── serializers.py        # Serialización de usuarios
│   │   │   └── urls.py               # /api/auth/*
│   │   │
│   │   ├── products/                 # Catálogo de productos
│   │   │   ├── models.py             # Category, Product, Stock
│   │   │   ├── views.py              # CRUD ViewSets
│   │   │   ├── serializers.py        # Serialización + stock
│   │   │   ├── urls.py               # /api/products/*
│   │   │   ├── admin.py              # Admin personalizado
│   │   │   └── management/commands/
│   │   │       └── seed.py           # Datos iniciales + imágenes
│   │   │
│   │   ├── orders/                   # Gestión de pedidos
│   │   │   ├── models.py             # Order, OrderItem (IVA/Nuvei)
│   │   │   ├── views.py              # Crear orden + pago + webhook
│   │   │   ├── serializers.py        # Validación de órdenes
│   │   │   ├── urls.py               # /api/orders/*
│   │   │   └── admin.py              # Admin con desglose fiscal
│   │   │
│   │   └── store_config/             # Configuración centralizada
│   │       ├── models.py             # StoreConfig (Singleton)
│   │       ├── views.py              # Config API + switch ambiente
│   │       ├── serializers.py        # Serialización
│   │       ├── urls.py               # /api/store-config/*
│   │       └── admin.py              # Admin agrupado por secciones
│   │
│   ├── config/                       # Configuración Django
│   │   ├── settings.py               # Settings principal
│   │   ├── urls.py                   # URLs raíz
│   │   ├── wsgi.py                   # WSGI entry point
│   │   └── asgi.py                   # ASGI entry point
│   │
│   ├── media/                        # Archivos multimedia (generado)
│   │   └── products/                 # Imágenes de productos
│   │
│   ├── .env                          # Variables de entorno
│   ├── requirements.txt              # Dependencias Python
│   ├── manage.py                     # CLI de Django
│   └── Dockerfile                    # Imagen Docker
│
├── payment-service/                  # Servicio 2: Node.js + Express
│   ├── src/
│   │   ├── index.ts                  # Entry point Express
│   │   ├── routes/
│   │   │   └── payment.routes.ts     # Rutas de pago
│   │   ├── controllers/
│   │   │   └── payment.controller.ts # Lógica de pagos
│   │   ├── services/
│   │   │   ├── linktopay.service.ts  # Servicio Link to Pay
│   │   │   ├── checkout.service.ts   # Servicio Checkout Modal
│   │   │   ├── nuvei-auth.service.ts # Autenticación HMAC Nuvei
│   │   │   ├── store-config.service.ts # Config desde Django
│   │   │   └── whatsapp.service.ts   # Generación de links WhatsApp
│   │   ├── middleware/               # Middlewares
│   │   ├── config/                   # Configuración
│   │   └── types/                    # Tipos TypeScript
│   │
│   ├── .env                          # Variables de entorno
│   ├── package.json                  # Dependencias Node.js
│   ├── tsconfig.json                 # Configuración TypeScript
│   └── Dockerfile                    # Imagen Docker
│
├── frontend/                         # Servicio 3: React + Vite
│   ├── src/
│   │   ├── App.jsx                   # Componente principal (tienda)
│   │   ├── App.css                   # Estilos del componente
│   │   ├── index.css                 # Design system global
│   │   ├── main.jsx                  # Entry point React
│   │   └── assets/                   # Assets estáticos
│   │
│   ├── public/
│   │   └── images/products/          # Imágenes de productos (14)
│   │
│   ├── index.html                    # HTML base
│   ├── vite.config.js                # Configuración Vite + proxies
│   ├── package.json                  # Dependencias React
│   └── Dockerfile                    # Imagen Docker
│
├── docker-compose.yml                # Orquestación Docker
├── .gitignore                        # Archivos ignorados por Git
└── DOCUMENTACION.md                  # Este documento
```

---

## Requisitos Previos

| Herramienta | Versión Mínima | Propósito |
|---|---|---|
| **Python** | 3.10+ | Backend Django |
| **Node.js** | 18+ | Payment Service y Frontend |
| **npm** | 8+ | Gestión de paquetes JS |
| **Git** | 2.x | Control de versiones |
| **Docker** (opcional) | 20+ | Despliegue con contenedores |

---

## Instalación y Configuración

### 1. Clonar el Repositorio

```bash
git clone https://github.com/Teban7u7/proyecto-licoreria-web-nuvei.git
cd proyecto-licoreria-web-nuvei
```

### 2. Backend (Django)

```bash
cd backend

# Crear entorno virtual (recomendado)
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Copiar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales de Nuvei

# Aplicar migraciones
python manage.py migrate

# Cargar datos iniciales (superusuario + productos + imágenes)
python manage.py seed
# Para reiniciar datos: python manage.py seed --reset
```

### 3. Payment Service (Node.js)

```bash
cd payment-service

# Instalar dependencias
npm install

# Copiar variables de entorno
cp .env.example .env
```

### 4. Frontend (React)

```bash
cd frontend

# Instalar dependencias
npm install
```

---

## Ejecución del Proyecto

Se requiere iniciar **3 terminales** simultáneamente:

### Terminal 1 — Backend Django (Puerto 8000)

```bash
cd backend
python manage.py runserver 8000
```

### Terminal 2 — Payment Service (Puerto 3001)

```bash
cd payment-service
npm run dev
```

### Terminal 3 — Frontend Vite (Puerto 5173)

```bash
cd frontend
npm run dev
```

### URLs activas:

| Servicio | URL | Descripción |
|---|---|---|
| **Tienda** | http://localhost:5173 | Interfaz de la licorería |
| **Admin Panel** | http://localhost:8000/admin | Panel de administración Django |
| **API REST** | http://localhost:8000/api/ | Endpoints del backend |
| **Payment Service** | http://localhost:3001/health | Health check del servicio de pagos |

### Ejecución con Docker (alternativa)

```bash
# Desde la raíz del proyecto
docker-compose up --build
```

Esto levanta automáticamente: PostgreSQL, Django, Payment Service y Frontend.

---

## Módulos del Backend (Django)

### 1. Accounts (`apps/accounts/`)

**Propósito**: Manejo de autenticación y usuarios administrativos.

| Componente | Descripción |
|---|---|
| **CustomUser** | Extiende AbstractUser con campos `phone` y `role` (admin/staff) |
| **JWT Auth** | Autenticación via tokens JWT (SimpleJWT) |
| **Registro** | Endpoint público para crear nuevos usuarios |

**Modelo CustomUser**:
- `username`, `email`, `password` (heredados de AbstractUser)
- `phone` — Teléfono del usuario
- `role` — `admin` o `staff`

---

### 2. Products (`apps/products/`)

**Propósito**: Gestión completa del catálogo de productos.

**Modelos**:

| Modelo | Campos Principales | Descripción |
|---|---|---|
| **Category** | `name`, `slug`, `description`, `image`, `is_active` | Categorías de productos (Whisky, Ron, Vodka, etc.) |
| **Product** | `category`, `name`, `brand`, `price`, `image`, `alcohol_content`, `volume_ml` | Producto individual |
| **Stock** | `product`, `quantity`, `min_quantity` | Control de inventario por producto |

**Productos Precargados (14)**:

| Categoría | Marca | Producto | Precio |
|---|---|---|---|
| Whisky | Highland Reserve | Black Label 12 Años | $42.50 |
| Whisky | Tennessee Oak | Classic No. 7 | $35.00 |
| Whisky | Royal Glen | Reserva 12 Años | $38.00 |
| Ron | Caribeño Dorado | Imperial Añejo 10 Años | $28.00 |
| Ron | Isla Dorada | Añejo 7 Años | $22.00 |
| Vodka | Nordic Frost | Original Premium | $20.00 |
| Vodka | Château Blanc | Ultra Premium | $45.00 |
| Vino | Valle Central | Cabernet Sauvignon Reserva | $12.00 |
| Vino | Costa Pacífico | Sauvignon Blanc Reserva | $10.00 |
| Cerveza | Sol Dorado | Lager Premium | $2.50 |
| Cerveza | Montaña | Pilsner Clásica | $1.50 |
| Gin | Sapphire Bay | London Dry Gin | $32.00 |
| Gin | Green Valley | London Dry Clásico | $28.00 |
| Especial | Nocturna | Edición Limitada Mystic | $19.00 |

> **Nota**: Todas las marcas son genéricas/ficticias para evitar conflictos con marcas registradas.

---

### 3. Orders (`apps/orders/`)

**Propósito**: Gestión del ciclo completo de pedidos con integración Nuvei.

**Modelo Order**:

| Campo | Tipo | Descripción |
|---|---|---|
| `customer_name` | CharField | Nombre del cliente |
| `customer_phone` | CharField | Teléfono (formato Ecuador: 593...) |
| `customer_email` | CharField | Email del cliente |
| `status` | Choices | `pending` → `payment_sent` → `paid` / `cancelled` / `refunded` |
| `subtotal` | Decimal | Base imponible (taxable_amount en Nuvei) |
| `vat_amount` | Decimal | Monto del IVA calculado |
| `tax_percentage` | Integer | Porcentaje de IVA (0%, 8%, 15%) |
| `total` | Decimal | Total a pagar (amount en Nuvei) |
| `payment_url` | URL | Enlace de pago generado por Link to Pay |
| `payment_status` | Choices | `pending` / `approved` / `rejected` / `cancelled` |
| `dev_reference` | CharField | Referencia única de la orden (ORD-XXXXXXXX) |
| `environment` | Choices | `STG` (Staging) / `PROD` (Producción) |

**Modelo OrderItem**:

| Campo | Descripción |
|---|---|
| `order` | FK a Order |
| `product` | FK a Product (PROTECT — no se puede eliminar producto con órdenes) |
| `quantity` | Cantidad solicitada |
| `unit_price` | Precio al momento de la compra |
| `subtotal` | quantity × unit_price (calculado automáticamente) |

---

### 4. Store Config (`apps/store_config/`)

**Propósito**: Configuración centralizada de la tienda (modelo Singleton).

**Secciones de Configuración**:

| Sección | Campos | Descripción |
|---|---|---|
| **Tienda** | `store_name` | Nombre de la tienda |
| **Ambiente** | `environment` | Switch STG ↔ PROD (un solo click) |
| **Credenciales STG** | `app_code_client/server`, `app_key_client/server` | Credenciales Nuvei Staging |
| **Credenciales PROD** | `app_code_client/server`, `app_key_client/server` | Credenciales Nuvei Producción |
| **Checkout Theme** | `checkout_logo_url`, `checkout_primary_color` | Personalización del modal de pago |
| **Fiscal** | `iva_percentage`, `default_installments_type` | Tarifa IVA y tipo de cuotas |
| **WhatsApp** | `whatsapp_number` | Número para envío de enlaces de pago |
| **Callbacks** | `webhook_url`, `success_url`, `failure_url`, `pending_url` | URLs de retorno Nuvei |

---

## Servicio de Pagos (Node.js)

El **Payment Service** es un microservicio en TypeScript/Express que actúa como intermediario entre Django y la API de Nuvei/Paymentez.

### Responsabilidades:
1. **Autenticación Nuvei**: Genera el token HMAC-SHA256 requerido por las APIs de Nuvei
2. **Link to Pay**: Crea enlaces de pago con QR para que el cliente pague
3. **Checkout Reference**: Inicializa una referencia para el modal de pago con tarjeta
4. **Webhook**: Recibe notificaciones de estado de transacciones desde Nuvei
5. **WhatsApp**: Genera enlaces para compartir el link de pago por WhatsApp

### Servicios internos:

| Servicio | Archivo | Función |
|---|---|---|
| `NuveiAuthService` | `nuvei-auth.service.ts` | Genera headers de autenticación HMAC |
| `LinkToPayService` | `linktopay.service.ts` | Genera enlaces Link to Pay via NocCAPI |
| `CheckoutService` | `checkout.service.ts` | Inicializa referencia de checkout via CCAPI |
| `WhatsAppService` | `whatsapp.service.ts` | Genera deep links de WhatsApp |
| `StoreConfigService` | `store-config.service.ts` | Obtiene configuración desde Django |

---

## Frontend (React + Vite)

### Componente Principal: `App.jsx`

La aplicación está construida como un SPA (Single Page Application) con las siguientes secciones:

### Secciones de la Interfaz

#### 1. Hero / Header
- Nombre de la tienda "NightDrop Licorería"
- Badge "Premium Delivery 24/7"
- Rating 4.9 y badge "Nuvei Secure"

#### 2. Catálogo de Productos (Grid)
- **Grid responsivo** que muestra todos los productos activos
- Cada tarjeta de producto incluye:
  - **Imagen del producto** (con fallback a ícono si no hay imagen)
  - **Marca** (texto en color primario)
  - **Nombre del producto**
  - **Badges**: Volumen (ml) y contenido alcohólico (%)
  - **Precio** en USD
  - **Botón "Añadir al Carrito"** (se resalta en hover)

#### 3. Carrito de Compras (Sidebar derecho)
- **Productos agregados** con imagen miniatura, nombre y precio
- **Controles de cantidad** (+/−) para cada producto
- **Formulario de datos del cliente**:
  - Nombre completo
  - Número de WhatsApp (formato 593...)
- **Desglose de precios**:
  - Subtotal
  - IVA (15%)
  - **Total**
- **Selector de método de pago**:
  - 🔗 **Link / QR** — Genera un enlace de pago + código QR
  - 💳 **Tarjeta** — Abre el modal de Nuvei Checkout
- **Botón "Confirmar Pedido"**

#### 4. Resultado del Pedido
Al confirmar el pedido exitosamente:
- Muestra referencia de la orden
- Si es **Link to Pay**: muestra QR escaneble + enlace de pago
- Si es **Checkout**: abre modal de pago con tarjeta

### Diseño y Estilo

El frontend utiliza un **diseño premium dark mode** con:
- **Glassmorphism** — Tarjetas con efecto de vidrio esmerilado
- **Gradientes** — Degradados de colores Nuvei (magenta → violeta)
- **Tipografía**: Plus Jakarta Sans (Google Fonts)
- **Animaciones**: Fade-in con delay escalonado, hover scale, rotación de imágenes
- **Paleta de colores**: Fondo oscuro `#0b0e14`, acento primario `#c800a1`

---

## Panel de Administración (Django Admin)

Accede al panel en: **http://localhost:8000/admin**

### Credenciales por defecto:
- **Usuario**: `admin`
- **Contraseña**: `admin1234`

### Secciones del Panel Admin:

#### Productos
1. **Categorías** (`/admin/products/category/`)
   - Ver, crear, editar y desactivar categorías
   - Campos: nombre, slug (auto-generado), descripción, imagen, activa

2. **Productos** (`/admin/products/product/`)
   - Lista con: nombre, marca, categoría, precio, stock, activo
   - Filtros por: categoría, marca, activo
   - Búsqueda por: nombre, marca, descripción
   - **Inline de Stock**: editar inventario directamente desde el producto
   - Imagen del producto (se sube a `media/products/`)

3. **Stock** (`/admin/products/stock/`)
   - Vista directa del inventario
   - Indicador visual de stock bajo (booleano)
   - Cantidad y cantidad mínima

#### Órdenes
4. **Órdenes** (`/admin/orders/order/`)
   - Lista con: referencia, cliente, total, IVA, estado, estado de pago, ambiente
   - Fieldsets organizados:
     - **Cliente**: nombre, teléfono, email
     - **Desglose Fiscal (Nuvei)**: subtotal, IVA, porcentaje, total, cuotas
     - **Estado**: estado de la orden, estado del pago, ambiente
     - **Nuvei**: URL de pago, transaction ID, referencia, LTP ID
   - Inline de items de la orden

#### Configuración
5. **Configuración de Tienda** (`/admin/store_config/storeconfig/`)
   - **Modelo Singleton** — Solo existe una instancia
   - Secciones colapsables:
     - Switch de Ambiente (STG ↔ PROD)
     - Credenciales Nuvei Staging y Producción
     - Tema del Checkout (logo, color primario)
     - IVA y tipo de cuotas
     - WhatsApp
     - URLs de callback

#### Usuarios
6. **Usuarios** (`/admin/accounts/customuser/`)
   - Gestión de usuarios administrativos
   - Roles: Administrador / Personal

---

## API REST — Endpoints

### Base URL: `http://localhost:8000/api/`

### Autenticación (`/api/auth/`)

| Método | Endpoint | Auth | Descripción |
|---|---|---|---|
| `POST` | `/api/auth/register/` | No | Registrar nuevo usuario |
| `POST` | `/api/auth/login/` | No | Obtener token JWT (access + refresh) |
| `POST` | `/api/auth/refresh/` | No | Refrescar token de acceso |
| `GET` | `/api/auth/profile/` | JWT | Obtener perfil del usuario autenticado |

**Ejemplo login**:
```json
POST /api/auth/login/
{
  "username": "admin",
  "password": "admin1234"
}
// Respuesta: { "access": "eyJ...", "refresh": "eyJ..." }
```

### Productos (`/api/products/`)

| Método | Endpoint | Auth | Descripción |
|---|---|---|---|
| `GET` | `/api/products/` | No | Listar productos activos (paginado) |
| `GET` | `/api/products/{id}/` | No | Detalle de un producto |
| `POST` | `/api/products/` | Admin | Crear producto |
| `PUT` | `/api/products/{id}/` | Admin | Actualizar producto |
| `DELETE` | `/api/products/{id}/` | Admin | Eliminar producto |
| `GET` | `/api/products/categories/` | No | Listar categorías |
| `GET` | `/api/products/categories/{slug}/` | No | Detalle de categoría |
| `GET` | `/api/products/stock/` | JWT | Ver stock |

**Filtros disponibles**: `?category=1`, `?is_active=true`, `?brand=Highland`
**Búsqueda**: `?search=whisky`
**Ordenamiento**: `?ordering=price`, `?ordering=-price`, `?ordering=name`

### Órdenes (`/api/orders/`)

| Método | Endpoint | Auth | Descripción |
|---|---|---|---|
| `POST` | `/api/orders/` | No | Crear orden + iniciar pago |
| `GET` | `/api/orders/` | JWT | Listar órdenes |
| `GET` | `/api/orders/{id}/` | JWT | Detalle de orden |
| `GET` | `/api/orders/latest/` | JWT | Última orden creada |
| `PUT` | `/api/orders/{id}/status/` | JWT | Cambiar estado de orden |
| `POST` | `/api/orders/webhook/` | No | Recibir webhook de Nuvei |

**Ejemplo crear orden**:
```json
POST /api/orders/
{
  "customer_name": "Esteban Álava",
  "customer_email": "esteban@test.com",
  "customer_phone": "593999888777",
  "payment_method": "linktopay",
  "installments_type": 0,
  "items": [
    { "product_id": 1, "quantity": 2 },
    { "product_id": 5, "quantity": 1 }
  ]
}
```

**Respuesta exitosa (Link to Pay)**:
```json
{
  "id": 1,
  "dev_reference": "ORD-A1B2C3D4",
  "status": "payment_sent",
  "subtotal": "107.00",
  "vat_amount": "16.05",
  "total": "123.05",
  "payment_url": "https://pay.paymentez.com/...",
  "nuvei_response": {
    "success": true,
    "data": {
      "payment": {
        "payment_url": "https://...",
        "payment_qr": "base64..."
      }
    }
  }
}
```

### Configuración (`/api/store-config/`)

| Método | Endpoint | Auth | Descripción |
|---|---|---|---|
| `GET` | `/api/store-config/` | No | Obtener configuración de la tienda |
| `PUT` | `/api/store-config/` | JWT | Actualizar configuración |
| `GET` | `/api/store-config/switch-env/` | JWT | Ver ambiente actual |
| `POST` | `/api/store-config/switch-env/` | JWT | Cambiar STG ↔ PROD |

---

## Flujo de Pago Nuvei

### Flujo Link to Pay (LTP)

```
1. Usuario agrega productos al carrito
2. Completa datos (nombre, teléfono)
3. Selecciona "Link / QR" como método de pago
4. Click en "Confirmar Pedido"
         │
         ▼
5. Frontend → POST /api/orders/ (Django)
         │
         ▼
6. Django:
   a. Crea la Orden + Items en BD
   b. Calcula subtotal + IVA + total
   c. Deduce stock de cada producto
   d. Envía request al Payment Service
         │
         ▼
7. Payment Service → POST /api/payments/link-to-pay
   a. Genera token HMAC-SHA256 con credenciales Nuvei
   b. Llama a Nuvei NocCAPI → /linktopay/init_order/
   c. Recibe payment_url + payment_qr
   d. Genera enlace de WhatsApp (opcional)
         │
         ▼
8. Django actualiza la orden con payment_url
9. Frontend muestra:
   - Código QR escaneable
   - Enlace directo de pago
         │
         ▼
10. Cliente escanea QR o abre enlace
11. Paga en la página de Nuvei
12. Nuvei envía webhook → /api/orders/webhook/
13. Django actualiza estado: paid / rejected
```

### Flujo Checkout Modal

```
1-4. Igual que LTP
         │
         ▼
5. Frontend → POST /api/orders/ (Django)
         │
         ▼
6. Django → Payment Service → /api/payments/checkout-reference
   a. Llama a Nuvei CCAPI → /v2/transaction/init_reference/
   b. Recibe reference (transacción)
         │
         ▼
7. Frontend abre el modal de Nuvei Checkout con la reference
8. Cliente ingresa datos de tarjeta en el modal seguro
9. Nuvei procesa el pago
10. Callback → actualización de estado
```

### Desglose Fiscal (Ecuador)

La integración con Nuvei Ecuador requiere desglose de impuestos:

| Campo Nuvei | Campo en Orden | Descripción |
|---|---|---|
| `amount` | `total` | Monto total a cobrar |
| `taxable_amount` | `subtotal` | Base imponible |
| `vat` | `vat_amount` | Monto del IVA |
| `tax_percentage` | `tax_percentage` | Porcentaje (0/8/15) |

**Fórmula**:
```
subtotal = Σ(precio_unitario × cantidad)
vat_amount = subtotal × (tax_percentage / 100)
total = subtotal + vat_amount
```

---

## Docker Compose

El archivo `docker-compose.yml` orquesta todos los servicios:

| Servicio | Puerto | Descripción |
|---|---|---|
| `db` | 5432 | PostgreSQL 16 Alpine |
| `django` | 8000 | Backend Django (auto-migra y seed) |
| `node` | 3001 | Payment Service (TypeScript) |
| `frontend` | 5173 | Vite dev server (React) |

```bash
# Levantar todo
docker-compose up --build

# Solo backend + DB
docker-compose up db django

# Ver logs de un servicio
docker-compose logs -f django
```

---

## Credenciales por Defecto

| Recurso | Usuario | Contraseña |
|---|---|---|
| **Django Admin** | `admin` | `admin1234` |
| **PostgreSQL (Docker)** | `user` | `password` |
| **Nuvei Staging** | `TEBANSTG-EC-CLIENT` | *(configurar en .env)* |

### Variables de Entorno Críticas

#### Backend (`.env`)
```env
DJANGO_SECRET_KEY=cambiar-en-produccion
NUVEI_APP_CODE_CLIENT_STG=TEBANSTG-EC-CLIENT
NUVEI_APP_KEY_CLIENT_STG=tu-app-key-client
NUVEI_APP_CODE_SERVER_STG=TEBANSTG-EC-SERVER
NUVEI_APP_KEY_SERVER_STG=tu-app-key-server
PAYMENT_SERVICE_URL=http://localhost:3001
```

#### Payment Service (`.env`)
```env
PORT=3001
DJANGO_API_URL=http://localhost:8000/api
PAYMENT_SERVICE_SECRET=internal-shared-secret
```

---

## Notas de Desarrollo

- **Base de datos local**: SQLite (archivo `db.sqlite3`). Se usa PostgreSQL en Docker.
- **Imágenes de productos**: Almacenadas en `frontend/public/images/products/` (estáticas) y `backend/media/products/` (dinámicas vía Django).
- **Proxy Vite**: Las rutas `/api` y `/media` se redirigen automáticamente al backend Django.
- **CORS**: Configurado para aceptar peticiones desde `localhost:3000`, `localhost:3001`, y `localhost:5173`.
- **JWT**: Token de acceso válido por 6 horas, refresh por 7 días.
- **Paginación**: API paginada con 20 resultados por página (`?page=2`).

---

*Documento generado el 21 de junio de 2026 — NightDrop Licorería v1.0*
