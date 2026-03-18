from datetime import datetime
import pyodbc

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


def get_connection():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost;"
        "DATABASE=RoseAmorDB;"
        "Trusted_Connection=yes;"
    )


def get_recent_orders():
    cn = get_connection()
    cursor = cn.cursor()

    cursor.execute("""
        SELECT TOP 10
            id,
            order_id,
            customer_id,
            sku,
            quantity,
            unit_price,
            order_date,
            channel,
            created_at
        FROM dbo.web_orders
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    cursor.close()
    cn.close()
    return rows


def customer_exists(customer_id: str) -> bool:
    cn = get_connection()
    cursor = cn.cursor()

    cursor.execute(
        "SELECT 1 FROM dbo.dim_customers WHERE customer_id = ?",
        (customer_id,)
    )
    row = cursor.fetchone()

    cursor.close()
    cn.close()
    return row is not None


def sku_exists(sku: str) -> bool:
    cn = get_connection()
    cursor = cn.cursor()

    cursor.execute(
        "SELECT 1 FROM dbo.dim_products WHERE sku = ?",
        (sku,)
    )
    row = cursor.fetchone()

    cursor.close()
    cn.close()
    return row is not None


@app.get("/", response_class=HTMLResponse)
def show_form(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "message": "",
            "error": "",
            "form_data": {
                "order_id": "",
                "customer_id": "",
                "sku": "",
                "quantity": "",
                "unit_price": "",
                "order_date": "",
                "channel": ""
            },
            "recent_orders": get_recent_orders()
        }
    )


@app.post("/save", response_class=HTMLResponse)
def save_order(
    request: Request,
    order_id: str = Form(...),
    customer_id: str = Form(...),
    sku: str = Form(...),
    quantity: int = Form(...),
    unit_price: float = Form(...),
    order_date: str = Form(...),
    channel: str = Form(...)
):
    message = ""
    error = ""

    form_data = {
        "order_id": order_id,
        "customer_id": customer_id,
        "sku": sku,
        "quantity": quantity,
        "unit_price": unit_price,
        "order_date": order_date,
        "channel": channel
    }

    try:
        order_id = order_id.strip()
        customer_id = customer_id.strip()
        sku = sku.strip()
        channel = channel.strip()

        if not order_id or not customer_id or not sku or not channel or not order_date:
            error = "Todos los campos son obligatorios."
            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "message": "",
                    "error": error,
                    "form_data": form_data,
                    "recent_orders": get_recent_orders()
                }
            )

        if len(order_id) > 20:
            error = "Order ID no puede superar los 20 caracteres."
            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "message": "",
                    "error": error,
                    "form_data": form_data,
                    "recent_orders": get_recent_orders()
                }
            )

        if len(customer_id) > 20:
            error = "Customer ID no puede superar los 20 caracteres."
            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "message": "",
                    "error": error,
                    "form_data": form_data,
                    "recent_orders": get_recent_orders()
                }
            )

        if len(sku) > 20:
            error = "SKU no puede superar los 20 caracteres."
            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "message": "",
                    "error": error,
                    "form_data": form_data,
                    "recent_orders": get_recent_orders()
                }
            )

        if len(channel) > 50:
            error = "Channel no puede superar los 50 caracteres."
            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "message": "",
                    "error": error,
                    "form_data": form_data,
                    "recent_orders": get_recent_orders()
                }
            )

        if quantity <= 0:
            error = "La cantidad debe ser mayor que cero."
            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "message": "",
                    "error": error,
                    "form_data": form_data,
                    "recent_orders": get_recent_orders()
                }
            )

        if unit_price <= 0:
            error = "El precio unitario debe ser mayor que cero."
            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "message": "",
                    "error": error,
                    "form_data": form_data,
                    "recent_orders": get_recent_orders()
                }
            )

        try:
            parsed_date = datetime.strptime(order_date, "%Y-%m-%d").date()
        except ValueError:
            error = "La fecha debe tener un formato válido."
            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "message": "",
                    "error": error,
                    "form_data": form_data,
                    "recent_orders": get_recent_orders()
                }
            )

        if not customer_exists(customer_id):
            error = "El customer_id no existe en dim_customers."
            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "message": "",
                    "error": error,
                    "form_data": form_data,
                    "recent_orders": get_recent_orders()
                }
            )

        if not sku_exists(sku):
            error = "El sku no existe en dim_products."
            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "message": "",
                    "error": error,
                    "form_data": form_data,
                    "recent_orders": get_recent_orders()
                }
            )

        cn = get_connection()
        cursor = cn.cursor()

        cursor.execute(
            """
            INSERT INTO dbo.web_orders
                (order_id, customer_id, sku, quantity, unit_price, order_date, channel)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (order_id, customer_id, sku, quantity, unit_price, parsed_date, channel)
        )

        cn.commit()
        cursor.close()
        cn.close()

        message = "Pedido registrado correctamente."
        form_data = {
            "order_id": "",
            "customer_id": "",
            "sku": "",
            "quantity": "",
            "unit_price": "",
            "order_date": "",
            "channel": ""
        }

    except Exception as ex:
        error = f"Error al guardar el pedido: {str(ex)}"

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "message": message,
            "error": error,
            "form_data": form_data,
            "recent_orders": get_recent_orders()
        }
    )