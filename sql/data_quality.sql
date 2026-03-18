--CREAR LA BD
CREATE DATABASE RoseAmorDB;
GO

-- Revisión de calidad de datos en tablas RAW

USE RoseAmorDB;
GO
-- 1. DUPLICADOS EN ORDERS
SELECT order_id, COUNT(*) 
FROM orders
GROUP BY order_id
HAVING COUNT(*) > 1;


-- 2. VALORES NULOS EN CAMPOS CLAVE (ORDERS)
SELECT *
FROM orders
WHERE order_id IS NULL
   OR customer_id IS NULL
   OR sku IS NULL;

-- 3. VALORES INVÁLIDOS (NEGATIVOS O CERO)
SELECT *
FROM orders
WHERE quantity <= 0
   OR unit_price <= 0;

-- 4. SKUs QUE NO EXISTEN EN PRODUCTS
SELECT o.*
FROM orders o
LEFT JOIN products p ON o.sku = p.sku
WHERE p.sku IS NULL;

-- 5. CLIENTES QUE NO EXISTEN EN CUSTOMERS
SELECT o.*
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL;

-- 6. PROBLEMAS EN CUSTOMERS
-- Nulos
SELECT *
FROM customers
WHERE customer_id IS NULL;

-- Duplicados
SELECT customer_id, COUNT(*)
FROM customers
GROUP BY customer_id
HAVING COUNT(*) > 1;

-- 7. PROBLEMAS EN PRODUCTS
-- Nulos o costos inválidos
SELECT *
FROM products
WHERE sku IS NULL
   OR cost IS NULL
   OR cost < 0;

-- Duplicados
SELECT sku, COUNT(*)
FROM products
GROUP BY sku
HAVING COUNT(*) > 1;