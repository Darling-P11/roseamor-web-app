
-- Creación de tablas STAGING (datos limpios)

USE RoseAmorDB;
GO


-- STAGING ORDERS
-- Filtra registros válidos
IF OBJECT_ID('stg_orders', 'U') IS NOT NULL DROP TABLE stg_orders;

SELECT *
INTO stg_orders
FROM orders
WHERE quantity > 0
  AND unit_price > 0;


-- STAGING PRODUCTS
-- Filtra costos válidos
IF OBJECT_ID('stg_products', 'U') IS NOT NULL DROP TABLE stg_products;

SELECT *
INTO stg_products
FROM products
WHERE cost >= 0;


-- STAGING CUSTOMERS
-- (Se asume que todos son válidos)
IF OBJECT_ID('stg_customers', 'U') IS NOT NULL DROP TABLE stg_customers;

SELECT *
INTO stg_customers
FROM customers;