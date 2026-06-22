# Memoria Técnica — Plataforma de Comercio Electrónico "NightDrop"

## Proyecto de Titulación: Implementación de E-commerce con Arquitectura de Microservicios e Integración de Pasarela de Pagos

---

## Tabla de Contenidos

1. [Equipo de Proyecto (Autores)](#1-equipo-de-proyecto-autores)
2. [Resumen del Proyecto](#2-resumen-del-proyecto)
3. [Contexto Académico y Justificación Tecnológica](#3-contexto-académico-y-justificación-tecnológica)
4. [Arquitectura del Sistema](#4-arquitectura-del-sistema)
5. [Estructura del Repositorio](#5-estructura-del-repositorio)
6. [Requisitos del Entorno](#6-requisitos-del-entorno)
7. [Instalación y Despliegue Local](#7-instalación-y-despliegue-local)
8. [Módulos del Backend (Django REST Framework)](#8-módulos-del-backend-django-rest-framework)
9. [Microservicio de Pagos (Node.js)](#9-microservicio-de-pagos-nodejs)
10. [Aplicación Cliente (React + Vite)](#10-aplicación-cliente-react--vite)
11. [Panel de Administración](#11-panel-de-administración)
12. [Especificación de la API REST](#12-especificación-de-la-api-rest)
13. [Flujo Transaccional de Pagos](#13-flujo-transaccional-de-pagos)
14. [Orquestación con Docker Compose](#14-orquestación-con-docker-compose)
15. [Variables de Entorno y Seguridad](#15-variables-de-entorno-y-seguridad)

---

## 1. Equipo de Proyecto (Autores)

Este proyecto de titulación es el resultado del esfuerzo conjunto y la investigación aplicada de los siguientes egresados de la Universidad Estatal de Milagro (UNEMI):

- **Esteban Alava** (`ealavav@unemi.edu.ec`) — *Lead Software Engineer*
  Encargado del diseño de la arquitectura central, toma de decisiones tecnológicas, estructuración del backend y orquestación general del sistema.
- **Geancarlo Barros** (`gbarrosa@unemi.edu.ec`) — *Co-Lead Software Engineer*
  Encargado del diseño e integración de microservicios, desarrollo del flujo transaccional en el frontend y validación de las pasarelas de pago.

Ambos autores colaboraron de manera equitativa y sinérgica en las fases de análisis, diseño, implementación y pruebas, garantizando la viabilidad y robustez de la plataforma.

---

## 2. Resumen del Proyecto

**NightDrop Licorería** es una plataforma de comercio electrónico desarrollada como proyecto de titulación. El sistema permite la gestión integral de un catálogo de productos, procesamiento de carritos de compras y la culminación de transacciones financieras mediante la integración de una pasarela de pagos externa.

### Características Principales:
- **Gestión de Catálogo**: Sistema de inventario categorizado con productos y control de stock.
- **Procesamiento de Órdenes**: Flujo completo desde la selección de productos hasta la confirmación de la orden.
- **Integración Financiera**: Conexión con entorno de pruebas (Sandbox) para simular transacciones reales.
- **Administración Centralizada**: Panel de control para la gestión operativa (productos, categorías, stock, parámetros fiscales).
- **Cálculo Tributario**: Implementación de lógica para el cálculo automático del Impuesto al Valor Agregado (IVA) aplicable en Ecuador.
- **Arquitectura Desacoplada**: Sistema dividido en tres servicios independientes (Frontend, Backend, Servicio de Pagos) para garantizar escalabilidad y mantenibilidad.

---

## 3. Contexto Académico y Justificación Tecnológica

Este proyecto fue concebido para demostrar competencias en el desarrollo de software moderno, empleando una arquitectura orientada a microservicios.

**Selección del Proveedor de Pagos (Nuvei/Paymentez):**
Para el componente transaccional, se optó por integrar la pasarela de pagos Nuvei (anteriormente Paymentez). Esta decisión responde estrictamente a fines académicos y de desarrollo. Nuvei provee un entorno de pruebas (Sandbox) público, accesible y bien documentado, lo cual resulta idóneo para validar la lógica de integración de pagos, la generación de tokens seguros (modalidad Link to Pay) y el manejo de webhooks (callbacks) sin la necesidad de establecer contratos comerciales preliminares ni incurrir en costos operativos durante la fase de desarrollo.

Es importante destacar que el proyecto no mantiene ninguna afiliación comercial o asociación directa con la entidad procesadora Nuvei. 

*Nota Operativa: Durante esta etapa del proyecto, la plataforma hace uso exclusivo de la modalidad "Link to Pay" (generación de un enlace de pago y un código QR transaccional). La integración directa de tarjetas de crédito o débito a través de un Checkout Modal nativo (que requeriría el uso de Credenciales de Cliente) no está implementada. En consecuencia, dichas credenciales han sido completamente omitidas del alcance y de la configuración del sistema para minimizar la superficie de exposición y mantener la simplicidad arquitectónica requerida para la tesis.*

---

## 4. Arquitectura del Sistema

El sistema implementa una arquitectura distribuida compuesta por tres nodos principales:

```text
┌─────────────────────────────────────────────────────────────────────┐
│                        CLIENTE (Navegador Web)                      │
│                     http://localhost:5173                           │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   FRONTEND (React+Vite)  │
                    │      Puerto: 5173        │
                    │                          │
                    │ - Presentación de UI     │
                    │ - Gestión de Estado Local│
                    │ - Consumo de API REST    │
                    └────────────┬─────────────┘
                                 │ Proxy Inverso local (/api, /media)
                    ┌────────────▼────────────┐
                    │   BACKEND (Django REST)   │
                    │      Puerto: 8000         │
                    │                           │
                    │ - Lógica de Negocio      │
                    │ - Persistencia (ORM)     │
                    │ - Panel de Administración│
                    │ - Seguridad (JWT)        │
                    └────────────┬──────────────┘
                                 │ Comunicación Interna (HTTP)
                    ┌────────────▼────────────┐
                    │  PAYMENT SERVICE (Node)   │
                    │      Puerto: 3001         │
                    │                           │
                    │ - Criptografía (HMAC)    │
                    │ - Proxy hacia Pasarela   │
                    │ - Recepción de Webhooks  │
                    └───────────────────────────┘
                                 │ Peticiones Firmadas Criptográficamente
                    ┌────────────▼────────────┐
                    │  PASARELA DE PAGOS API    │
                    │  (Entorno Sandbox / STG)  │
                    └───────────────────────────┘
```

---

## 5. Estructura del Repositorio

La organización del código fuente refleja la separación de responsabilidades:

```text
proyecto-titulacion/
├── backend/                          # Capa Lógica y de Datos (Python/Django)
│   ├── apps/
│   │   ├── accounts/                 # Gestión de identidades y control de acceso (JWT)
│   │   ├── products/                 # Gestión de inventario (Categorías, Productos, Stock)
│   │   ├── orders/                   # Gestión transaccional y desglose fiscal
│   │   └── store_config/             # Parámetros globales del sistema (Patrón Singleton)
│   ├── config/                       # Configuraciones núcleo del framework
│   └── manage.py                     # Interfaz de línea de comandos de Django
│
├── payment-service/                  # Microservicio de Integración (Node.js/Express/TypeScript)
│   ├── src/
│   │   ├── controllers/              # Controladores de enlace (LinkToPay) y webhooks
│   │   ├── services/                 # Lógica de encriptación y peticiones HTTP
│   │   └── routes/                   # Definición de rutas del microservicio
│   └── package.json                  # Dependencias del entorno Node
│
├── frontend/                         # Capa de Presentación (React/Vite)
│   ├── src/                          # Componentes React, hojas de estilo (CSS)
│   ├── public/                       # Activos estáticos e imágenes del catálogo
│   └── vite.config.js                # Configuración de empaquetado y proxy de desarrollo
│
└── docker-compose.yml                # Manifiesto de orquestación de contenedores
```

---

## 6. Requisitos del Entorno

Para la ejecución local y evaluación del proyecto, se requiere el siguiente stack tecnológico:

| Tecnología | Versión Recomendada | Propósito en el Proyecto |
|---|---|---|
| **Python** | 3.10 o superior | Entorno de ejecución para el Backend (Django) |
| **Node.js** | 18 LTS o superior | Entorno de ejecución para Frontend y Payment Service |
| **Gestor de Paquetes** | npm 8+ o pip | Instalación de dependencias (JS y Python) |
| **Git** | 2.x | Control de versiones del código fuente |
| **Docker** (Opcional) | 20+ | Para despliegue aislado mediante contenedores |

---

## 7. Instalación y Despliegue Local

### 7.1. Clonación del Repositorio

```bash
git clone https://github.com/Teban7u7/proyecto-licoreria-web-nuvei.git
cd proyecto-licoreria-web-nuvei
```

### 7.2. Configuración del Backend (Capa de Negocio)

```bash
cd backend
python -m venv venv
# Activación del entorno virtual
# Windows: venv\Scripts\activate
# Unix/MacOS: source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env  # Configure variables posteriormente

# Ejecución de migraciones de base de datos
python manage.py migrate

# Población de la base de datos (Seed de productos de prueba y usuario administrador)
python manage.py seed
```

### 7.3. Configuración del Servicio de Pagos

```bash
cd ../payment-service
npm install
cp .env.example .env
```

### 7.4. Configuración del Frontend

```bash
cd ../frontend
npm install
```

### 7.5. Puesta en Marcha

Se requiere la ejecución concurrente de los tres servicios. Abra tres terminales independientes:

```bash
# Terminal 1: Backend
cd backend && python manage.py runserver 8000

# Terminal 2: Microservicio de Pagos
cd payment-service && npm run dev

# Terminal 3: Cliente Web
cd frontend && npm run dev
```

**Accesos del Sistema:**
- **Aplicación Web**: `http://localhost:5173`
- **Panel Administrativo**: `http://localhost:8000/admin`
- **API REST**: `http://localhost:8000/api/`

---

## 8. Módulos del Backend (Django REST Framework)

El backend está estructurado en cuatro aplicaciones principales (`apps/`), garantizando la cohesión y bajo acoplamiento:

### 8.1. Módulo `accounts`
Responsable de la autenticación y autorización.
- **Modelado**: Implementa un `CustomUser` extendiendo el modelo base de Django, añadiendo atributos como `phone` y `role` (Administrador/Staff).
- **Seguridad**: Emplea JSON Web Tokens (JWT) para la gestión de sesiones sin estado (stateless).

### 8.2. Módulo `products`
Gestiona el catálogo expuesto al consumidor.
- **Modelos**: `Category`, `Product`, y `Stock`.
- **Reglas de Negocio**: Control de inventario en tiempo real. Los productos están vinculados a categorías y poseen metadatos específicos (volumen, grado alcohólico). La semilla (`seed`) provee 14 productos con marcas genéricas para pruebas.

### 8.3. Módulo `orders`
Maneja el ciclo de vida de la transacción.
- **Modelos**: `Order` (cabecera) y `OrderItem` (detalle).
- **Lógica Fiscal**: Implementa el cálculo de la base imponible (`subtotal`), cálculo del IVA aplicable (`vat_amount`) según el porcentaje vigente, y la totalización.
- **Trazabilidad**: Almacena el identificador de transacción (`dev_reference`) y el estado financiero (`payment_status`) actualizado vía webhooks.

### 8.4. Módulo `store_config`
Centraliza los parámetros globales empleando el patrón de diseño Singleton (una única instancia en base de datos).
- Permite modificar de manera dinámica parámetros como:
  - Nombre del comercio.
  - Credenciales de servidor (Server Key) para la firma de peticiones (HMAC).
  - Porcentaje de IVA aplicable.
  - Entorno de ejecución (Sandbox/Producción).

---

## 9. Microservicio de Pagos (Node.js)

Se implementó un microservicio intermedio para desacoplar la complejidad criptográfica y la comunicación con APIs externas del backend principal.

### Funciones Principales:
1. **Firma Criptográfica**: Genera tokens de autenticación (HMAC-SHA256) requeridos por el proveedor, combinando la llave secreta del servidor (Server Key), la fecha y los datos de la transacción.
2. **Generación de Enlaces (Link to Pay)**: Se comunica con la API externa para solicitar un URL de pago y un código QR que se presentarán al usuario.
3. **Recepción de Callbacks (Webhooks)**: Escucha asíncronamente las notificaciones de la pasarela de pagos cuando una transacción cambia de estado (aprobada, rechazada) y notifica al Backend.

*Nota Técnica: Este servicio requiere y administra exclusivamente las claves de servidor (Server Keys).*

---

## 10. Aplicación Cliente (React + Vite)

El frontend está desarrollado como una Single Page Application (SPA), optimizada mediante el empaquetador Vite.

### Interfaz de Usuario (UI/UX)
- **Diseño**: Implementa un esquema de color oscuro ("Dark Mode") con efectos visuales modernos (Glassmorphism) para una percepción profesional.
- **Catálogo**: Visualización en cuadrícula (grid) adaptativa, mostrando imagen, especificaciones técnicas y precio de los artículos.
- **Carrito de Compras**: Gestor de estado que permite actualizar cantidades y visualizar el desglose fiscal (Subtotal e IVA) en tiempo real.
- **Flujo Transaccional**: Al confirmar la orden, el cliente recibe un código QR y un hipervínculo para proceder con la transacción en el entorno Sandbox.

---

## 11. Panel de Administración

El sistema provee una interfaz administrativa (backoffice) generada dinámicamente mediante Django Admin, accesible en `/admin`.

**Credenciales de Acceso (Entorno Local):**
- **Usuario**: `admin`
- **Contraseña**: `admin1234`

### Capacidades del Administrador:
- **Gestión de Inventario**: Creación y modificación de productos, ajuste manual de stock e inserción de imágenes descriptivas.
- **Monitorización de Órdenes**: Visualización del estado de los pedidos, detalle de los montos calculados y revisión del estado de pago notificado por la pasarela.
- **Configuración Global**: Modificación de las llaves del servidor (Server Credentials), ajuste de tasas impositivas y URLs de retorno.

---

## 12. Especificación de la API REST

El Backend expone una API RESTful para el consumo del cliente y de servicios internos. (URL Base: `http://localhost:8000/api/`)

| Recurso | Método HTTP | Ruta | Descripción | Auth Requerida |
|---|---|---|---|---|
| **Autenticación** | `POST` | `/auth/login/` | Obtención de tokens JWT | No |
| **Catálogo** | `GET` | `/products/` | Listado paginado de productos | No |
| **Catálogo** | `GET` | `/products/{id}/` | Detalle específico de un ítem | No |
| **Transacción** | `POST` | `/orders/` | Creación de orden e inicio de pago | No |
| **Administración** | `GET` | `/orders/` | Historial de órdenes generadas | Sí (JWT) |
| **Webhooks** | `POST` | `/orders/webhook/` | Recepción de estado de transacción | No |

---

## 13. Flujo Transaccional de Pagos

El flujo de pago asíncrono ("Link to Pay") sigue el siguiente ciclo de vida:

1. **Creación**: El cliente confirma el carrito de compras en el Frontend.
2. **Registro**: El Frontend envía el objeto (payload) a `/api/orders/` del Backend.
3. **Persistencia**: El Backend valida el stock, calcula impuestos, guarda la orden con estado "Pendiente" y descuenta el inventario reservado temporalmente.
4. **Solicitud de Pago**: El Backend delega la petición al Payment Service (Node.js).
5. **Criptografía**: El Payment Service firma la petición usando el `Server Key` y se contacta con la pasarela externa (Sandbox).
6. **Respuesta**: La pasarela devuelve un enlace de pago (URL) y un código QR.
7. **Presentación**: El Frontend muestra el QR/URL al cliente.
8. **Interacción**: El cliente accede al enlace seguro e interactúa con el entorno de pruebas para simular el pago.
9. **Notificación (Webhook)**: Tras el procesamiento, la pasarela dispara un Webhook asíncrono (HTTP POST) al Payment Service.
10. **Conciliación**: El sistema procesa el webhook y actualiza el estado de la orden (Pagado/Rechazado) en la base de datos de manera definitiva.

---

## 14. Orquestación con Docker Compose

Para asegurar la reproducibilidad del entorno y facilitar despliegues integrales, se provee un archivo `docker-compose.yml`.

```bash
# Construcción y levantamiento concurrente de todos los contenedores
docker-compose up --build
```
Los servicios orquestados son:
- `db`: Motor de base de datos relacional PostgreSQL.
- `django`: Capa lógica expuesta en el puerto 8000.
- `node`: Microservicio de integración financiera expuesto en el puerto 3001.
- `frontend`: Servidor de aplicación Vite expuesto en el puerto 5173.

---

## 15. Variables de Entorno y Seguridad

El sistema utiliza archivos `.env` para la inyección de configuraciones sensibles, mitigando el riesgo de exposición en repositorios de código.

**Configuraciones Críticas (Backend - `.env`):**
```env
DJANGO_SECRET_KEY=clave_criptografica_privada
# Las llaves de servidor son requeridas para la modalidad Link to Pay
NUVEI_APP_CODE_SERVER_STG=CODIGO_ASIGNADO_AL_COMERCIO
NUVEI_APP_KEY_SERVER_STG=LLAVE_PRIVADA_DEL_SERVIDOR
PAYMENT_SERVICE_URL=http://localhost:3001
```

**Configuraciones Críticas (Payment Service - `.env`):**
```env
PORT=3001
DJANGO_API_URL=http://localhost:8000/api
PAYMENT_SERVICE_SECRET=secreto_interno_para_comunicacion_microservicios
```

---

*Memoria Técnica generada en el marco de Proyecto de Titulación.*
