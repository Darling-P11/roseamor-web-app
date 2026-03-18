
-- Tabla para registrar pedidos desde la app web


USE RoseAmorDB;
GO

IF OBJECT_ID('dbo.web_orders', 'U') IS NOT NULL
    DROP TABLE dbo.web_orders;
GO

CREATE TABLE dbo.web_orders (
    id INT IDENTITY(1,1) PRIMARY KEY,
    order_id VARCHAR(20) NOT NULL,
    customer_id VARCHAR(20) NOT NULL,
    sku VARCHAR(20) NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(18,2) NOT NULL CHECK (unit_price > 0),
    order_date DATE NOT NULL,
    channel VARCHAR(50) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT GETDATE()
);
GO