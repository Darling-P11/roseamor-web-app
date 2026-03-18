
-- Creación de dimensiones y tabla de hechos

USE RoseAmorDB;
GO


-- DIMENSIÓN CLIENTES
IF OBJECT_ID('dim_customers', 'U') IS NOT NULL DROP TABLE dim_customers;

SELECT DISTINCT
    customer_id,
    name,
    country,
    segment
INTO dim_customers
FROM stg_customers;


-- DIMENSIÓN PRODUCTOS
IF OBJECT_ID('dim_products', 'U') IS NOT NULL DROP TABLE dim_products;

SELECT DISTINCT
    sku,
    category,
    cost
INTO dim_products
FROM stg_products;


-- TABLA DE HECHOS (FACT_ORDERS)
IF OBJECT_ID('fact_orders', 'U') IS NOT NULL DROP TABLE fact_orders;

SELECT
    o.order_id,
    o.customer_id,
    o.sku,
    o.quantity,
    o.unit_price,
    o.order_date,
    o.channel,

    -- Métricas calculadas
    (o.quantity * o.unit_price) AS total_sales,
    (o.quantity * (o.unit_price - p.cost)) AS margin

INTO fact_orders
FROM stg_orders o
JOIN dim_products p ON o.sku = p.sku;