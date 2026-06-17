import asyncio
import random
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Path, Request


# ---------------------------------------------------------------------------
# State — 10 fake products, 3 warehouses
# ---------------------------------------------------------------------------

WAREHOUSES = [
    {"id": 507, "name": "Москва (Коледино)"},
    {"id": 117986, "name": "Санкт-Петербург (Уткина Заводь)"},
    {"id": 686, "name": "Краснодар (Тихорецкая)"},
]

PRODUCTS: dict[str, dict] = {
    str(1000 + i): {
        "nmID": 1000 + i,
        "vendorCode": str(1000 + i),
        "title": f"Товар WB {i + 1}",
        "description": f"Описание товара WB {i + 1}",
        "dimensions": {"length": 10 + i, "width": 8, "height": 5, "weightBrutto": 0.5 + i * 0.05},
        "sizes": [{"skus": [f"200{1000 + i:06d}"]}],
        "characteristics": [{"id": 88953, "value": 0.5 + i * 0.05}],
        "photos": [{"big": f"https://images.wb.ru/big/new/{1000 + i}.jpg"}],
        "price": round(500.0 + i * 100, 2),
        "discount": random.randint(0, 20),
        "updatedAt": "2024-01-01T00:00:00",
    }
    for i in range(10)
}

# barcode → vendorCode
BARCODE_TO_SKU: dict[str, str] = {
    f"200{1000 + i:06d}": str(1000 + i) for i in range(10)
}

# warehouse_id → {barcode: qty}
WH_BARCODE_STOCKS: dict[int, dict[str, int]] = {
    wh["id"]: {bc: random.randint(5, 60) for bc in BARCODE_TO_SKU}
    for wh in WAREHOUSES
}

# warehouse_name → {vendorCode: qty}
SUPPLIER_STOCKS: dict[str, dict[str, int]] = {
    wh["name"]: {sku: random.randint(5, 60) for sku in PRODUCTS}
    for wh in WAREHOUSES
}


# ---------------------------------------------------------------------------
# Drift — ±2% prices, ±3 units stocks, runs every 60 s
# ---------------------------------------------------------------------------

def _drift() -> None:
    for product in PRODUCTS.values():
        product["price"] = max(100.0, round(product["price"] * random.uniform(0.98, 1.02), 2))

    for wh_stocks in SUPPLIER_STOCKS.values():
        for sku in wh_stocks:
            wh_stocks[sku] = max(0, wh_stocks[sku] + random.randint(-3, 3))

    for bc_stocks in WH_BARCODE_STOCKS.values():
        for bc in bc_stocks:
            bc_stocks[bc] = max(0, bc_stocks[bc] + random.randint(-3, 3))


async def _background_drift() -> None:
    while True:
        await asyncio.sleep(60)
        _drift()


@asynccontextmanager
async def lifespan(_: FastAPI):
    asyncio.create_task(_background_drift())
    yield


app = FastAPI(lifespan=lifespan)


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

@app.get("/open-utils/tokens/introspect-v2")
async def introspect():
    return {"Ok": True, "payload": {"type": "seller"}}


# ---------------------------------------------------------------------------
# Cards (content-api.wildberries.ru)
# ---------------------------------------------------------------------------

@app.post("/content/v2/get/cards/list")
async def get_cards_list(request: Request):
    body = await request.json()
    limit = body.get("settings", {}).get("cursor", {}).get("limit", 100)
    cards = list(PRODUCTS.values())
    page = cards[:limit]
    last = page[-1] if page else {}
    return {
        "cards": page,
        "cursor": {
            "total": len(page),
            "nmID": last.get("nmID", 0),
            "updatedAt": last.get("updatedAt", "2024-01-01T00:00:00"),
        },
    }


@app.post("/content/v2/cards/update")
async def update_cards(request: Request):
    body = await request.json()
    for item in body:
        sku = item.get("vendorCode")
        if sku in PRODUCTS:
            p = PRODUCTS[sku]
            p["title"] = item.get("title", p["title"])
            p["description"] = item.get("description", p["description"])
            p["dimensions"] = item.get("dimensions", p["dimensions"])
    return {}


@app.get("/content/v2/cards/error/list")
async def cards_error_list():
    return {"data": []}


# ---------------------------------------------------------------------------
# Prices (discounts-prices-api.wildberries.ru)
# ---------------------------------------------------------------------------

@app.get("/api/v2/list/goods/filter")
async def list_goods_filter(limit: int = 100, offset: int = 0):
    items = list(PRODUCTS.values())[offset: offset + limit]
    goods = [
        {
            "nmID": p["nmID"],
            "vendorCode": p["vendorCode"],
            "discount": p["discount"],
            "sizes": [
                {
                    "price": p["price"],
                    "discountedPrice": round(p["price"] * (1 - p["discount"] / 100), 2),
                }
            ],
        }
        for p in items
    ]
    return {"data": {"listGoods": goods}}


@app.post("/api/v2/upload/task")
async def upload_price_task(request: Request):
    body = await request.json()
    for item in body.get("data", []):
        nm_id = item.get("nmID")
        for p in PRODUCTS.values():
            if p["nmID"] == nm_id:
                if "price" in item:
                    p["price"] = float(item["price"])
                if "discount" in item:
                    p["discount"] = int(item["discount"])
    task_id = random.randint(10000, 99999)
    return {"data": {"id": task_id}}


@app.get("/api/v2/history/tasks")
async def history_tasks(uploadID: int = 0):
    return {
        "data": {
            "uploadID": uploadID,
            "status": "done",
            "overAllGoodsNumber": len(PRODUCTS),
            "successGoodsNumber": len(PRODUCTS),
        }
    }


# ---------------------------------------------------------------------------
# Warehouses (supplies-api.wildberries.ru)
# ---------------------------------------------------------------------------

@app.get("/api/v1/warehouses")
async def get_warehouses():
    return [{"ID": wh["id"], "name": wh["name"]} for wh in WAREHOUSES]


# ---------------------------------------------------------------------------
# Stocks (statistics-api.wildberries.ru)
# ---------------------------------------------------------------------------

@app.get("/api/v1/supplier/stocks")
async def get_supplier_stocks(dateFrom: str = "2000-01-01"):
    result = []
    for wh_name, wh_stocks in SUPPLIER_STOCKS.items():
        for sku, qty in wh_stocks.items():
            result.append(
                {
                    "supplierArticle": sku,
                    "warehouseName": wh_name,
                    "quantity": qty,
                    "quantityFull": qty,
                }
            )
    return result


@app.get("/api/v1/supplier/orders")
async def get_orders(dateFrom: str = "2024-08-01"):
    return []


# ---------------------------------------------------------------------------
# Per-warehouse stocks (marketplace-api.wildberries.ru)
# ---------------------------------------------------------------------------

@app.post("/api/v3/stocks/{warehouse_id}")
async def get_stocks_on_warehouse(warehouse_id: int = Path(...), request: Request = None):
    body = await request.json()
    barcodes: list[str] = body.get("skus", [])
    bc_stocks = WH_BARCODE_STOCKS.get(warehouse_id, {})
    stocks = [{"sku": bc, "amount": bc_stocks.get(bc, 0)} for bc in barcodes]
    return {"stocks": stocks}


# ---------------------------------------------------------------------------
# Analytics / Turnover (seller-analytics-api.wildberries.ru)
# ---------------------------------------------------------------------------

@app.post("/api/v2/stocks-report/products/groups")
async def stocks_report(request: Request):
    body = await request.json()
    nm_ids: list[int] = body.get("nmIDs", [])
    items = [
        {
            "nmID": nm_id,
            "metrics": {
                "avgStockTurnover": {"hours": round(random.uniform(24, 720), 1)},
                "saleRate": {"hours": round(random.uniform(1, 48), 1)},
            },
        }
        for nm_id in nm_ids
    ]
    return {"data": {"groups": [{"items": items}]}}
