# RoseAmor – Prueba Técnica Full Stack Data Engineer

## 1. Descripción general

En esta prueba técnica desarrollé una solución de punta a punta para transformar datos crudos en una base confiable para análisis, generar un dashboard en Power BI y construir una aplicación web simple para registrar pedidos.

La solución parte de tres archivos CSV:

- `orders.csv`
- `customers.csv`
- `products.csv`

A partir de esos archivos se realizó un proceso de carga, validación, limpieza, modelado y consumo analítico en SQL Server 2022. Posteriormente, se construyó un dashboard en Power BI con los KPIs solicitados y una aplicación web en FastAPI conectada a la misma base de datos para registrar nuevos pedidos con validaciones.

El objetivo fue diseñar una solución funcional, clara y fácil de mantener, siguiendo un flujo similar al que se usaría en un entorno real de datos y reporting.

---

## 2. Arquitectura y flujo de datos

La arquitectura implementada sigue una separación simple entre datos crudos, datos limpiados y capa de consumo analítico.

### Flujo general

```text
Archivos CSV (raw)
        ↓
Importación manual en SQL Server
        ↓
Tablas base: orders, customers, products
        ↓
Validación de calidad de datos
        ↓
Tablas staging: stg_orders, stg_customers, stg_products
        ↓
Modelo dimensional:
    - dim_customers
    - dim_products
    - fact_orders
        ↓
Consumo analítico:
    - consultas SQL (KPIs)
    - dashboard en Power BI
        ↓
App web:
    - inserción de nuevos pedidos en web_orders
    
---

## Explicación del flujo

Primero importé los archivos CSV a SQL Server usando el asistente de importación de archivos planos de SSMS. Esa importación generó las tablas base `orders`, `customers` y `products`, que funcionan como capa raw dentro de esta solución.

Después ejecuté consultas de diagnóstico para revisar la calidad de la información. Con base en esos hallazgos, generé tablas de staging (`stg_orders`, `stg_customers`, `stg_products`) con los datos ya filtrados y consistentes.

Luego construí el modelo dimensional con dos dimensiones (`dim_customers` y `dim_products`) y una tabla de hechos (`fact_orders`), que fue la base utilizada tanto para los KPIs en SQL como para el dashboard de Power BI.

Finalmente, agregué una aplicación web desarrollada en FastAPI para registrar nuevos pedidos en una tabla independiente llamada `web_orders`, incluyendo validaciones de negocio y persistencia en SQL Server.

---

## 3. Estructura del repositorio

```text
roseamor-fullstack-data/
│
├── data/
│   └── raw/
│       ├── orders.csv
│       ├── customers.csv
│       └── products.csv
│
├── sql/
│   ├── 01_data_quality.sql
│   ├── 02_staging.sql
│   ├── 03_dim_fact.sql
│   ├── kpis.sql
│   └── web_orders.sql
│
├── dashboard/
│   └── RoseAmor_Dashboard.pbix
│
├── app/
│   ├── main.py
│   ├── requirements.txt
│   ├── static/
│   │   └── styles.css
│   └── templates/
│       └── index.html
│
└── README.md

## 4. Limpieza y calidad de datos

Antes de construir el modelo analítico, revisé la calidad de los datos importados para identificar problemas que pudieran afectar los KPIs y el dashboard.

### 4.1 Revisión realizada

Se revisaron los siguientes aspectos:

- duplicados en `orders`
- valores nulos en campos clave
- cantidades o precios inválidos
- integridad de `customer_id`
- integridad de `sku`
- nulos o costos inválidos en `products`
- duplicados en `customers` y `products`

---

### 4.2 Problemas encontrados

Durante la revisión encontré los siguientes casos:

#### a) Duplicados en `orders`

Al revisar `order_id`, aparecieron valores repetidos. En este caso no asumí inmediatamente que se trataba de un error, porque en muchos escenarios un mismo `order_id` puede aparecer varias veces si representa diferentes líneas de un mismo pedido.  

Por esa razón, los pedidos no se eliminaron automáticamente solo por repetición del identificador.

---

#### b) Valores inválidos en `orders`

Se encontraron registros con:

- `quantity <= 0`
- `unit_price <= 0`

Estos registros sí afectan directamente los cálculos de ventas, ticket promedio y margen, por lo que fueron excluidos al construir la tabla `stg_orders`.

---

#### c) Integridad referencial

Se verificó si existían pedidos con `customer_id` que no estuvieran en `customers` y si había pedidos con `sku` que no existieran en `products`.  

En la revisión realizada no aparecieron inconsistencias de este tipo, lo cual permitió construir el modelo sin necesidad de correcciones adicionales en esa parte.

---

#### d) Problemas en `products`

Se encontraron productos con costo negativo o costo nulo. Como el costo es un valor esencial para calcular el margen, esos registros fueron excluidos al construir `stg_products`.

---

#### e) Fechas inválidas

Durante el desarrollo del dashboard en Power BI se detectó que algunos valores de `order_date` no se interpretaban correctamente como fecha o incluían datos inconsistentes.  

Para evitar errores en la visualización temporal, se trabajó con columnas validadas en Power BI para separar y ordenar correctamente el análisis por mes.

---

### 4.3 Decisiones tomadas

Las decisiones de limpieza fueron las siguientes:

- excluir registros de `orders` con cantidades o precios no válidos  
- excluir registros de `products` con costos negativos  
- mantener `customers` completos porque no presentaban problemas críticos  
- conservar la estructura de pedidos tal como venía en el archivo, asumiendo que un `order_id` repetido puede representar múltiples líneas del mismo pedido  
- validar fechas y agrupación temporal desde Power BI para asegurar la visualización correcta por mes  

---

### 4.4 Justificación

Estas decisiones se tomaron para evitar que métricas como ventas totales, margen y ticket promedio se distorsionaran por datos inconsistentes.  

El objetivo no fue modificar arbitrariamente la información, sino asegurar que la capa analítica trabaje con datos confiables y coherentes con el negocio.

## 5. Modelo de datos

Después de limpiar los datos, organicé la información en un modelo tipo estrella, porque es una estructura simple, eficiente y adecuada para reporting y BI.

---

### 5.1 Tablas base

Las tablas base importadas desde los CSV fueron:

- `orders`
- `customers`
- `products`

Estas tablas representan la capa inicial de datos crudos.

---

### 5.2 Tablas staging

A partir de las tablas base, construí las siguientes tablas de staging:

- `stg_orders`
- `stg_customers`
- `stg_products`

#### `stg_orders`

Contiene únicamente pedidos con:

- `quantity > 0`
- `unit_price > 0`

---

#### `stg_products`

Contiene únicamente productos con:

- `cost >= 0`

---

#### `stg_customers`

Se generó como copia de `customers`, ya que no fue necesario aplicar filtros de calidad adicionales.

---

### 5.3 Dimensiones

#### `dim_customers`

Incluye la información descriptiva de clientes, como:

- `customer_id`
- `name`
- `country`
- `segment`

Esta tabla se usa para análisis por cliente y segmentación geográfica.

---

#### `dim_products`

Incluye la información descriptiva de productos, como:

- `sku`
- `category`
- `cost`

Esta tabla se usa para análisis por producto y categoría.

---

### 5.4 Tabla de hechos

#### `fact_orders`

Esta es la tabla central del modelo analítico e incluye:

- `order_id`
- `customer_id`
- `sku`
- `quantity`
- `unit_price`
- `order_date`
- `channel`
- `total_sales`
- `margin`

---

### Métricas calculadas

Las métricas se calcularon directamente en la construcción de la tabla de hechos:

- `total_sales = quantity * unit_price`
- `margin = quantity * (unit_price - cost)`

Esto permite que el modelo quede listo para consumo analítico sin necesidad de cálculos adicionales.

---

### 5.5 Relaciones

El modelo trabaja con las siguientes relaciones lógicas:

- `fact_orders.customer_id → dim_customers.customer_id`
- `fact_orders.sku → dim_products.sku`

En Power BI estas relaciones fueron configuradas como relaciones de muchos a uno desde la tabla de hechos hacia cada dimensión, lo cual permitió filtrar correctamente el dashboard por cliente, país, producto y categoría.

## 6. Consultas SQL y KPIs

Se generaron varios archivos `.sql` con las consultas principales solicitadas para análisis.

### KPIs calculados

- ventas totales  
- margen total  
- número de pedidos  
- ticket promedio  

---

### Consultas adicionales

También se incluyeron consultas para:

- ventas por mes  
- ventas por canal  
- margen por categoría  
- top 10 clientes por ingresos  
- top 10 productos más vendidos  

Estas consultas sirven tanto como validación del modelo como apoyo para contrastar los resultados mostrados en el dashboard.

---

##  7. Dashboard en Power BI

Se desarrolló un dashboard en Power BI basado en las siguientes tablas:

- `fact_orders`  
- `dim_customers`  
- `dim_products`  

---

###  Elementos incluidos

#### KPIs principales

- Ventas Totales  
- Margen Total  
- Número de Pedidos  
- Ticket Promedio  

---

####  Visualizaciones

- Ventas por mes  
- Ventas por canal  
- Margen por categoría  
- Top 10 clientes por ingresos  
- Top 10 productos más vendidos  

---

####  Filtros

- rango de fecha  
- canal  
- categoría  
- país  

---

### Archivo del dashboard

El archivo se encuentra en:

```text
dashboard/RoseAmor_Dashboard.pbix

## 8. Aplicación web para registrar pedidos

Además del procesamiento analítico, desarrollé una aplicación web simple para registrar pedidos de forma manual.

---

### 8.1 Tecnologías utilizadas

- Python 3.12  
- FastAPI  
- Jinja2  
- pyodbc  
- SQL Server 2022  
- HTML + CSS  

---

### 8.2 Funcionalidad

La aplicación permite ingresar un nuevo pedido con los siguientes campos:

- `order_id`  
- `customer_id`  
- `sku`  
- `quantity`  
- `unit_price`  
- `order_date`  
- `channel`  

---

### 8.3 Validaciones implementadas

Se implementaron validaciones tanto en frontend como en backend para evitar errores al guardar en SQL Server.

#### Validaciones aplicadas

- campos obligatorios  
- `quantity > 0`  
- `unit_price > 0`  
- longitud máxima para campos de texto  
- formato válido de fecha  
- verificación de existencia de `customer_id` en `dim_customers`  
- verificación de existencia de `sku` en `dim_products`  

---

## 8.4 Persistencia

Los datos ingresados desde la aplicación web se guardan en la tabla:

**dbo.web_orders**

Esta tabla es independiente de **fact_orders**, ya que su propósito en esta prueba es demostrar la captura de datos desde una interfaz web conectada a SQL Server, sin alterar directamente la capa analítica previamente construida.

---

## 8.5 Dónde queda guardada la data

Todos los pedidos registrados desde la web quedan almacenados en **SQL Server 2022**, dentro de la base de datos **RoseAmorDB**, específicamente en la tabla:

**dbo.web_orders**

Para verificarlos, se puede ejecutar:

```sql
SELECT *
FROM dbo.web_orders
ORDER BY id DESC;

## 9. Cómo ejecutar la solución en otra computadora

A continuación detallo los pasos para ejecutar este proyecto desde cero en otra máquina.

---

### 9.1 Requisitos previos

Es necesario tener instalado:

- SQL Server 2022  
- SQL Server Management Studio (SSMS)  
- Python 3.12  
- Power BI Desktop  
- Git (opcional, para clonar el repositorio)  

---

### 9.2 Paso 1: clonar o descargar el repositorio

    git clone [URL_DEL_REPOSITORIO]

O descargarlo como archivo ZIP y extraerlo.

### 9.3 Paso 2: crear la base de datos

Abrir SSMS y ejecutar:

    CREATE DATABASE RoseAmorDB;
    GO

Luego:

    USE RoseAmorDB;
    GO

### 9.4 Paso 3: importar los CSV

Importar manualmente los archivos `orders.csv`, `customers.csv` y `products.csv` usando el asistente de importación de archivos planos de SSMS para crear las tablas:

- `orders`
- `customers`
- `products`

### 9.5 Paso 4: ejecutar scripts SQL

Ejecutar en este orden los archivos dentro de `sql/`:

- `01_data_quality.sql`
- `02_staging.sql`
- `03_dim_fact.sql`
- `kpis.sql`
- `web_orders.sql`

Con esto quedarán creadas las tablas staging, dimensiones, hechos y la tabla de captura web.

### 9.6 Paso 5: ejecutar la aplicación web

Abrir una terminal dentro de la carpeta `app/` y ejecutar:

    python -m venv venv

Activar el entorno virtual en Windows PowerShell:

    venv\Scripts\Activate.ps1

Instalar dependencias:

    pip install -r requirements.txt

Ejecutar la aplicación:

    uvicorn main:app --reload

Abrir en el navegador:

    http://127.0.0.1:8000

### 9.7 Paso 6: abrir el dashboard

Abrir el archivo:

    dashboard/RoseAmor_Dashboard.pbix

Si fuera necesario, actualizar la conexión hacia la base de datos local `RoseAmorDB`.
## 10. Cómo actualizar la solución si llega un CSV nuevo

Si mañana llega una nueva versión de los archivos CSV, el proceso de actualización sería el siguiente.

### 10.1 Reemplazar archivos raw

Reemplazar los archivos antiguos dentro de:

    data/raw/

por los nuevos archivos.

### 10.2 Reimportar a SQL Server

Volver a importar los archivos en las tablas base:

- `orders`
- `customers`
- `products`

Dependiendo del escenario, esto puede hacerse truncando y recargando las tablas o recreándolas desde cero.

### 10.3 Volver a ejecutar la capa de transformación

Ejecutar nuevamente:

- `02_staging.sql`
- `03_dim_fact.sql`

Con esto se regeneran las tablas limpias y el modelo dimensional con la nueva información.

### 10.4 Refrescar consultas y dashboard

Ejecutar `kpis.sql` si se desea validar resultados por SQL y luego abrir Power BI para actualizar el modelo y refrescar el dashboard.

### 10.5 Aplicación web

La aplicación web no necesita cambios para seguir funcionando, ya que registra pedidos en `web_orders`. Solo depende de que la base `RoseAmorDB` exista y que las dimensiones usadas para validación (`dim_customers` y `dim_products`) estén actualizadas.

---

## 11. Decisiones técnicas

Durante el desarrollo de la prueba tomé las siguientes decisiones técnicas:

### SQL Server 2022

Elegí SQL Server 2022 porque permite trabajar cómodamente con importación de datos, transformación, modelado y consultas analíticas, además de integrarse bien con Power BI.

### Modelo estrella

Opté por un esquema estrella porque es una estructura simple y efectiva para reporting, facilita la navegación del modelo y mejora la claridad del análisis.

### FastAPI

Desarrollé la aplicación web en FastAPI porque la vacante menciona Python para ETL/APIs y porque permite construir una solución rápida, limpia y funcional con validaciones claras.

### Tabla web_orders separada

Decidí guardar los registros de la app en una tabla separada (`web_orders`) para no alterar directamente la tabla de hechos construida a partir de los CSV originales. Esto mantiene separada la captura manual de la capa analítica principal.

### Validaciones dobles

Implementé validaciones tanto en el formulario como en el backend, para reducir errores de entrada y proteger la persistencia en la base de datos.