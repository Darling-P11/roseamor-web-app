
-- Consultas analíticas y KPIs

USE RoseAmorDB;
GO

-- 1. VENTAS TOTALES
SELECT SUM(total_sales) AS total_sales
FROM fact_orders;


-- 2. TOTAL DE PEDIDOS
SELECT COUNT(DISTINCT order_id) AS total_orders
FROM fact_orders;


-- 3. TICKET PROMEDIO
SELECT 
    SUM(total_sales) / COUNT(DISTINCT order_id) AS avg_ticket
FROM fact_orders;

-- 4. MARGEN TOTAL
SELECT SUM(margin) AS total_margin
FROM fact_orders;


-- 5. VENTAS POR MES
SELECT 
    FORMAT(order_date, 'yyyy-MM') AS month,
    SUM(total_sales) AS total_sales
FROM fact_orders
GROUP BY FORMAT(order_date, 'yyyy-MM')
ORDER BY month;


-- 6. VENTAS POR CANAL
SELECT 
    channel,
    SUM(total_sales) AS total_sales
FROM fact_orders
GROUP BY channel;


-- 7. MARGEN POR CATEGORÍA
SELECT 
    p.category,
    SUM(f.margin) AS total_margin
FROM fact_orders f
JOIN dim_products p ON f.sku = p.sku
GROUP BY p.category;


-- 8. TOP 10 CLIENTES
SELECT TOP 10
    customer_id,
    SUM(total_sales) AS total_sales
FROM fact_orders
GROUP BY customer_id
ORDER BY total_sales DESC;


-- 9. TOP 10 PRODUCTOS
SELECT TOP 10
    sku,
    SUM(quantity) AS total_quantity
FROM fact_orders
GROUP BY sku
ORDER BY total_quantity DESC;