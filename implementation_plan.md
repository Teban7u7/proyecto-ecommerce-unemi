# 🍷 Plan de Implementación — Backend Licorería Virtual (Ecuador)

## Pasarela de Pagos: Nuvei (Paymentez) Ecuador

> [!IMPORTANT]
> Se integran **3 productos Nuvei**: Link to Pay (ahora), Checkout (ahora) y Debit with Token (futuro)

## Arquitectura General

```mermaid
graph TB
    subgraph "Cliente / Frontend"
        A[Frontend / Postman]
    end
    
    subgraph "Backend Principal - Django REST Framework"
        B[API REST - Productos/Categorías/Stock]
        C[Admin Panel - Gestión]
        D[Auth - JWT]
        E[Config Manager - STG/PROD Switch]
    end
    
    subgraph "Microservicio Pagos - Node.js/TypeScript"
        F[Nuvei Integration Service]
        G[Link to Pay Generator]
        H[Checkout Reference Generator]
        I[WhatsApp Link Builder]
        J[Webhook Handler]
    end
    
    subgraph "Base de Datos"
        K[(PostgreSQL)]
    end
    
    subgraph "Nuvei / Paymentez"
        L[Link to Pay API]
        M[Checkout SDK]
        N[Debit with Token API - Futuro]
    end
    
    A --> B
    A --> F
    B --> K
    F --> K
    E --> F
    G --> L
    H --> M
    I --> |wa.me link| A
    J --> L
```

## Stack Tecnológico

| Componente | Tecnología | Propósito |
|---|---|---|
| Backend Core | Django 5 + DRF | API REST, Admin, Auth |
| Microservicio Pagos | Node.js + TypeScript + Express | Nuvei integration, Links de pago |
| Base de Datos | PostgreSQL 16 | Persistencia de datos |
| ORM | Django ORM + Prisma (Node) | Acceso a BD |
| Auth | JWT (djangorestframework-simplejwt) | Autenticación |
| Pasarela de Pagos | Nuvei/Paymentez Ecuador | Cobros |
| Deploy | Render.com | Hosting |

---

## Nuvei API — Detalles Técnicos

### Ambientes / Endpoints

| Ambiente | Cards API Base URL | Cash/LinkToPay/Wallets Base URL |
|---|---|---|
| **Staging (STG)** | `https://ccapi-stg.paymentez.com` | `https://noccapi-stg.paymentez.com` |
| **Production (PROD)** | `https://ccapi.paymentez.com` | `https://noccapi.paymentez.com` |

### Autenticación (Auth-Token)

Todas las peticiones requieren header `Auth-Token`. Se construye así:

```
Auth-Token = base64(APPLICATION_CODE;UNIX_TIMESTAMP;SHA256_HASH)
```

Donde:
```python
SHA256_HASH = sha256(APP_KEY + UNIX_TIMESTAMP).hexdigest()
AUTH_TOKEN = base64(f"{APP_CODE};{UNIX_TIMESTAMP};{SHA256_HASH}")
```

> [!WARNING]  
> Las credenciales de STG y PROD son **diferentes**. Cada ambiente tiene su propio `Application Code` y `App Key` para Client y Server.

### Credenciales requeridas (por ambiente)

| Credencial | Uso |
|---|---|
| `APP_CODE_CLIENT` | Tokenización frontend (Checkout SDK) |
| `APP_KEY_CLIENT` | Tokenización frontend |
| `APP_CODE_SERVER` | Peticiones backend (Link to Pay, Debit) |
| `APP_KEY_SERVER` | Peticiones backend |

---

### Desglose de IVA — Ecuador

> [!IMPORTANT]
> Nuvei requiere que el IVA se pase **desglosado** en cada transacción. Ecuador maneja tasas de **0%**, **8%** y **15%**.

| Campo | Tipo | Descripción |
|---|---|---|
| `amount` | `number` | **Total a pagar** (base + IVA incluido) |
| `vat` | `number` | Monto calculado del IVA |
| `taxable_amount` | `number` | Base imponible (antes de impuestos) |
| `tax_percentage` | `number` | Porcentaje de IVA: `0`, `8` o `15` |
| `installments_type` | `number` | `0` = Corriente, `2` = Con intereses, `3` = Sin intereses |
| `currency` | `string` | `"USD"` para Ecuador |

**Ejemplo de cálculo:**
```
Base imponible (taxable_amount): $40.00
IVA 15% (vat):                   $6.00
Total (amount):                  $46.00
tax_percentage:                  15
```

### Objeto `conf` — Personalización del Checkout

Todas las llamadas a `init_reference` deben incluir el arreglo `conf` con la versión de estilos v2 y el theme de la licorería:

```json
{
  "conf": {
    "style_version": "2",
    "theme": {
      "logo": "https://cdn.paymentez.com/img/nv/nuvei_logo.png",
      "primary_color": "#C800A1"
    }
  }
}
```

> [!NOTE]
> El `logo` y `primary_color` se pueden personalizar con la marca de tu licorería. Se configuran desde `StoreConfig` en el admin.

---

### 1. Link to Pay API (Generación de enlaces)

**Endpoint:** `POST /linktopay/init_order/`

```
STG: https://noccapi-stg.paymentez.com/linktopay/init_order/
PROD: https://noccapi.paymentez.com/linktopay/init_order/
```

**Request Body:**
```json
{
  "user": {
    "id": "customer_123",
    "email": "cliente@email.com",
    "name": "Juan",
    "last_name": "Pérez"
  },
  "order": {
    "dev_reference": "ORD-001",
    "description": "Pedido Licorería - Whisky JW Black Label",
    "amount": 46.00,
    "vat": 6.00,
    "taxable_amount": 40.00,
    "tax_percentage": 15,
    "installments_type": 0,
    "currency": "USD"
  },
  "configuration": {
    "partial_payment": false,
    "expiration_days": 1,
    "allowed_payment_methods": ["All"],
    "success_url": "https://tudominio.com/pago-exitoso",
    "failure_url": "https://tudominio.com/pago-fallido",
    "pending_url": "https://tudominio.com/pago-pendiente",
    "review_url": "https://tudominio.com/pago-revision"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "order": {
      "id": "8REV4qMyevlR4xGm3OL",
      "status": "Init"
    },
    "payment": {
      "payment_url": "https://link-stg.paymentez.com/checkout/8REV4qMyevlR4xGm3OL",
      "payment_qr": "base64_qr_image..."
    }
  }
}
```

> El `payment_url` es lo que se envía al cliente por WhatsApp.

### 2. Checkout (Modal de pago — Frontend) — API v3

**Flujo:**
1. Backend genera `reference` via `POST /v3/transaction/init_reference/`
2. Frontend abre modal con SDK `PaymentCheckout`
3. Modal maneja el pago completo (PCI compliant)

**Init Reference Endpoint (v3):**
```
STG: https://ccapi-stg.paymentez.com/v3/transaction/init_reference/
PROD: https://ccapi.paymentez.com/v3/transaction/init_reference/
```

**Request Body:**
```json
{
  "user": {
    "id": "customer_123",
    "email": "cliente@email.com"
  },
  "order": {
    "dev_reference": "ORD-001",
    "description": "Pedido Licorería - Whisky JW Black Label",
    "amount": 46.00,
    "vat": 6.00,
    "taxable_amount": 40.00,
    "tax_percentage": 15,
    "installments_type": 0,
    "currency": "USD"
  },
  "conf": {
    "style_version": "2",
    "theme": {
      "logo": "https://tu-licoreria.com/logo.png",
      "primary_color": "#C800A1"
    }
  }
}
```

**Checkout SDK (Frontend):**
```javascript
let paymentCheckout = new PaymentCheckout.modal({
  env_mode: "stg", // "stg" o "prod" — controlado por el switch
  onResponse: function(response) {
    // response.transaction.status: "success" | "failure"
    // response.transaction.id: "CB-81011"
    // response.transaction.status_detail: 3
  }
});

paymentCheckout.open({
  reference: 'REFERENCE_FROM_BACKEND'
});
```

### 3. Debit with Token (Futuro) — API v3

**Endpoint (v3):**
```
STG: https://ccapi-stg.paymentez.com/v3/transaction/debit/
PROD: https://ccapi.paymentez.com/v3/transaction/debit/
```

**Request:**
```json
{
  "user": { "id": "customer_123", "email": "cliente@email.com" },
  "order": {
    "amount": 46.00,
    "vat": 6.00,
    "taxable_amount": 40.00,
    "tax_percentage": 15,
    "description": "Pedido recurrente",
    "dev_reference": "ORD-REC-001",
    "installments_type": 0,
    "currency": "USD"
  },
  "card": { "token": "SAVED_CARD_TOKEN" }
}
```

### 4. Webhook (Notificación de pagos)

Nuvei envía HTTP POST a tu `callback_url` cuando una transacción es aprobada o cancelada:

```json
{
  "transaction": {
    "status": "1",
    "status_detail": "3",
    "id": "CI-502",
    "dev_reference": "ORD-001",
    "amount": "45.50",
    "paid_date": "26/04/2026 10:30:00",
    "stoken": "e03f67eba6d730d8468f328961ac9b2e",
    "application_code": "AppCode",
    "ltp_id": "LeNgJbx57Vnj9Rnq"
  },
  "user": { "id": "customer_123", "email": "cliente@email.com" },
  "card": { "bin": "411111", "type": "vi", "number": "1111" }
}
```

**Validación stoken:**
```python
stoken = md5(f"{transaction_id}_{app_code}_{user_id}_{app_key}")
```

---

## Estructura del Proyecto

```
proyecto-titulacion/
├── backend/                          # Django Backend
│   ├── manage.py
│   ├── requirements.txt
│   ├── config/
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── staging.py
│   │   │   └── production.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── apps/
│   │   ├── products/                 # CRUD productos
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── admin.py
│   │   │   └── filters.py
│   │   ├── orders/                   # Órdenes
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   └── signals.py
│   │   ├── accounts/                 # Autenticación
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   └── urls.py
│   │   └── store_config/            # Switch STG/PROD
│   │       ├── models.py
│   │       ├── serializers.py
│   │       ├── views.py
│   │       └── urls.py
│   └── Dockerfile
│
├── payment-service/                  # Node.js/TypeScript
│   ├── package.json
│   ├── tsconfig.json
│   ├── prisma/
│   │   └── schema.prisma
│   ├── src/
│   │   ├── index.ts
│   │   ├── config/
│   │   │   └── nuvei.config.ts      # STG/PROD endpoints & creds
│   │   ├── routes/
│   │   │   ├── payment.routes.ts
│   │   │   └── webhook.routes.ts
│   │   ├── controllers/
│   │   │   ├── linktopay.controller.ts
│   │   │   ├── checkout.controller.ts
│   │   │   └── webhook.controller.ts
│   │   ├── services/
│   │   │   ├── nuvei-auth.service.ts   # Auth-Token builder
│   │   │   ├── linktopay.service.ts    # Link to Pay API
│   │   │   ├── checkout.service.ts     # Checkout init_reference
│   │   │   └── whatsapp.service.ts     # wa.me link builder
│   │   ├── middleware/
│   │   │   ├── auth.middleware.ts
│   │   │   └── error.middleware.ts
│   │   └── types/
│   │       └── nuvei.types.ts
│   └── Dockerfile
│
├── docker-compose.yml
├── .env.example
└── README.md
```

## Modelos de Datos

### Products App
- **Category**: `id`, `name`, `slug`, `description`, `image`, `is_active`, `created_at`
- **Product**: `id`, `category(FK)`, `name`, `slug`, `description`, `price`, `image`, `alcohol_content`, `volume_ml`, `brand`, `is_active`, `created_at`, `updated_at`
- **Stock**: `id`, `product(1to1)`, `quantity`, `min_quantity`, `last_restocked`, `updated_at`

### Orders App
- **Order**: `id`, `customer_name`, `customer_phone`, `customer_email`, `status`, `subtotal(taxable_amount)`, `vat_amount`, `tax_percentage(0/8/15)`, `total(amount)`, `payment_url`, `payment_status`, `nuvei_transaction_id`, `dev_reference`, `ltp_id`, `installments_type(0/2/3)`, `environment(STG/PROD)`, `created_at`, `updated_at`
- **OrderItem**: `id`, `order(FK)`, `product(FK)`, `quantity`, `unit_price`, `subtotal`

### Accounts App
- **CustomUser**: Extiende AbstractUser + `phone`, `role(admin/staff)`

### Store Config App
- **StoreConfig** (Singleton):
  - `store_name`
  - `environment` → `STG` | `PROD` (el switch)
  - `nuvei_app_code_client_stg`, `nuvei_app_key_client_stg`
  - `nuvei_app_code_server_stg`, `nuvei_app_key_server_stg`
  - `nuvei_app_code_client_prod`, `nuvei_app_key_client_prod`
  - `nuvei_app_code_server_prod`, `nuvei_app_key_server_prod`
  - `whatsapp_number`
  - `iva_percentage` → `0`, `8` o `15` (tasas Ecuador)
  - `default_installments_type` → `0` (Corriente), `2` (Con Int), `3` (Sin Int)
  - `checkout_logo_url` (para `conf.theme.logo`)
  - `checkout_primary_color` (para `conf.theme.primary_color`)
  - `webhook_url`
  - `success_url`, `failure_url`, `pending_url`
  - `updated_at`, `updated_by`

## Switch STG ↔ PROD — Flujo

```mermaid
sequenceDiagram
    participant Admin
    participant Django as Django API
    participant Config as StoreConfig DB
    participant Node as Node.js Service
    participant Nuvei as Nuvei API

    Admin->>Django: POST /api/store-config/switch-env/
    Note right of Admin: {"environment": "PROD"}
    Django->>Config: Update environment = "PROD"
    Django-->>Admin: ✅ Switched to PROD
    
    Note over Admin,Nuvei: Siguiente pago...
    
    Admin->>Django: POST /api/orders/ (crear orden)
    Django->>Node: POST /api/payments/create-link
    Node->>Config: Read current environment
    Config-->>Node: environment="PROD", creds_prod
    Node->>Node: Build Auth-Token with PROD creds
    Node->>Nuvei: POST noccapi.paymentez.com/linktopay/init_order/
    Nuvei-->>Node: payment_url (PROD)
    Node-->>Django: { paymentLink, whatsappLink }
```

## Flujo de Pago con Link to Pay + WhatsApp

```mermaid
sequenceDiagram
    participant Client as Cliente
    participant Django as Django API
    participant Node as Node.js Service
    participant Nuvei as Nuvei API
    participant WS as WhatsApp

    Client->>Django: POST /api/orders/
    Django->>Django: Validar stock, calcular total + IVA
    Django->>Node: POST /api/payments/create-link
    Node->>Node: Leer config STG/PROD
    Node->>Node: Construir Auth-Token
    Node->>Nuvei: POST /linktopay/init_order/
    Nuvei-->>Node: { payment_url, payment_qr }
    Node->>Node: Generar wa.me link
    Note right of Node: wa.me/593XXX?text=Paga aquí: payment_url
    Node-->>Django: { paymentUrl, whatsappLink, orderId }
    Django->>Django: Guardar orden con payment_url
    Django-->>Client: Orden creada + links
    
    Client->>WS: Envía link de pago al cliente
    Note over WS: Cliente paga en el link
    Nuvei->>Node: Webhook POST (pago aprobado)
    Node->>Node: Validar stoken
    Node->>Django: Actualizar estado orden
```

## Endpoints API

### Django REST API (Puerto 8000)

| Método | Endpoint | Descripción | Auth |
|---|---|---|---|
| `POST` | `/api/auth/register/` | Registro admin | No |
| `POST` | `/api/auth/login/` | Login JWT | No |
| `POST` | `/api/auth/refresh/` | Refresh token | No |
| `GET` | `/api/products/` | Listar productos | No |
| `POST` | `/api/products/` | Crear producto | Admin |
| `GET` | `/api/products/{id}/` | Detalle producto | No |
| `PUT` | `/api/products/{id}/` | Actualizar producto | Admin |
| `DELETE` | `/api/products/{id}/` | Eliminar producto | Admin |
| `GET` | `/api/categories/` | Listar categorías | No |
| `POST` | `/api/categories/` | Crear categoría | Admin |
| `PUT` | `/api/categories/{id}/` | Actualizar categoría | Admin |
| `DELETE` | `/api/categories/{id}/` | Eliminar categoría | Admin |
| `GET` | `/api/stock/` | Ver stock | Admin |
| `PUT` | `/api/stock/{id}/` | Actualizar stock | Admin |
| `GET` | `/api/orders/` | Listar órdenes | Admin |
| `POST` | `/api/orders/` | Crear orden + generar link | No |
| `GET` | `/api/orders/{id}/` | Detalle orden | Admin |
| `PUT` | `/api/orders/{id}/status/` | Cambiar estado | Admin |
| `GET` | `/api/store-config/` | Ver configuración | Admin |
| `PUT` | `/api/store-config/` | Actualizar config | Admin |
| `POST` | `/api/store-config/switch-env/` | **Switch STG↔PROD** | Admin |

### Node.js Payment Service (Puerto 3001)

| Método | Endpoint | Descripción |
|---|---|---|
| `POST` | `/api/payments/link-to-pay` | Generar Link to Pay Nuvei |
| `POST` | `/api/payments/checkout-reference` | Generar referencia para Checkout |
| `POST` | `/api/payments/whatsapp-link` | Generar link wa.me con payment URL |
| `GET` | `/api/payments/status/{id}` | Consultar estado transacción |
| `POST` | `/api/webhooks/nuvei` | Webhook notificación Nuvei |

## Variables de Entorno (.env)

```env
# Django
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/licoreria_db

# Nuvei Staging
NUVEI_APP_CODE_CLIENT_STG=your-client-app-code-stg
NUVEI_APP_KEY_CLIENT_STG=your-client-app-key-stg
NUVEI_APP_CODE_SERVER_STG=your-server-app-code-stg
NUVEI_APP_KEY_SERVER_STG=your-server-app-key-stg

# Nuvei Production
NUVEI_APP_CODE_CLIENT_PROD=your-client-app-code-prod
NUVEI_APP_KEY_CLIENT_PROD=your-client-app-key-prod
NUVEI_APP_CODE_SERVER_PROD=your-server-app-code-prod
NUVEI_APP_KEY_SERVER_PROD=your-server-app-key-prod

# Nuvei API URLs
NUVEI_CCAPI_STG=https://ccapi-stg.paymentez.com
NUVEI_CCAPI_PROD=https://ccapi.paymentez.com
NUVEI_NOCCAPI_STG=https://noccapi-stg.paymentez.com
NUVEI_NOCCAPI_PROD=https://noccapi.paymentez.com

# WhatsApp
WHATSAPP_BUSINESS_NUMBER=593XXXXXXXXX

# Node Payment Service
PAYMENT_SERVICE_URL=http://localhost:3001
PAYMENT_SERVICE_SECRET=internal-shared-secret

# IVA Ecuador
IVA_PERCENTAGE=15

# Callback URLs
SUCCESS_URL=https://tudominio.com/pago-exitoso
FAILURE_URL=https://tudominio.com/pago-fallido
PENDING_URL=https://tudominio.com/pago-pendiente
```

## Fases de Desarrollo

### Fase 1: Setup y Modelos ✅
- [x] Investigar Nuvei API (Link to Pay, Checkout, Debit with Token)
- [ ] Inicializar proyecto Django
- [ ] Configurar PostgreSQL
- [ ] Crear modelos de datos
- [ ] Migraciones

### Fase 2: API REST Django
- [ ] CRUD Categorías
- [ ] CRUD Productos
- [ ] Gestión de Stock
- [ ] Sistema de Órdenes
- [ ] Autenticación JWT
- [ ] Store Config + Switch STG/PROD

### Fase 3: Microservicio de Pagos (Node.js/TypeScript)
- [ ] Setup Express + TypeScript + Prisma
- [ ] Nuvei Auth-Token builder service
- [ ] Link to Pay integration
- [ ] Checkout init_reference integration
- [ ] WhatsApp link generator (wa.me)
- [ ] Webhook handler + stoken validation

### Fase 4: Testing y Deploy
- [ ] Tests con Nuvei Staging (tarjetas de prueba)
- [ ] Configurar Render.com (Django + Node.js + PostgreSQL)
- [ ] Docker setup
- [ ] Deploy
