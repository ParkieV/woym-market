import asyncio
import random
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request


# ---------------------------------------------------------------------------
# State — 10 fake products
# ---------------------------------------------------------------------------

PRODUCTS: dict[str, dict] = {
    f"SKU-{i + 1:04d}": {
        "product_id": 10000 + i,
        "offer_id": f"SKU-{i + 1:04d}",
        "name": f"Товар Ozon {i + 1}",
        "description": f"Описание товара Ozon {i + 1}",
        "price": round(700.0 + i * 150, 2),
        "marketing_price": round(800.0 + i * 150, 2),
        "old_price": round(850.0 + i * 150, 2),
        "min_price": round(500.0 + i * 100, 2),
        "barcodes": [f"3000{10000 + i}"],
        "search_words": f"товар ozon {i + 1}",
        # market_sku is the FBO sku Ozon assigns; use product_id for simplicity
        "market_sku": 10000 + i,
    }
    for i in range(10)
}

STOCKS: dict[str, int] = {sku: random.randint(5, 80) for sku in PRODUCTS}

WAREHOUSE_NAME = "moskva_rfc"  # _validate_warehouse_name → "Moskva Rfc"


# ---------------------------------------------------------------------------
# Drift — ±2% prices, ±3 units stocks, every 60 s
# ---------------------------------------------------------------------------

def _drift() -> None:
    for p in PRODUCTS.values():
        p["price"] = max(100.0, round(p["price"] * random.uniform(0.98, 1.02), 2))

    for sku in STOCKS:
        STOCKS[sku] = max(0, STOCKS[sku] + random.randint(-3, 3))


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
# Product list  (pagination: return all on first call, empty on second)
# ---------------------------------------------------------------------------

@app.post("/v3/product/list")
async def product_list(request: Request):
    body = await request.json()
    last_id = body.get("last_id", None)
    if last_id:
        return {"result": {"items": [], "last_id": "", "total": 0}}
    items = [{"product_id": p["product_id"], "offer_id": p["offer_id"]} for p in PRODUCTS.values()]
    return {"result": {"items": items, "last_id": "end", "total": len(items)}}


# ---------------------------------------------------------------------------
# Product info list (v3/product/info/list)
# ---------------------------------------------------------------------------

@app.post("/v3/product/info/list")
async def product_info_list(request: Request):
    body = await request.json()
    offer_ids: list[str] = body.get("offer_id", list(PRODUCTS.keys()))
    items = []
    for oid in offer_ids:
        p = PRODUCTS.get(oid)
        if not p:
            continue
        items.append(
            {
                "offer_id": p["offer_id"],
                "name": p["name"],
                "primary_image": [f"https://cdn.ozon.ru/img/{p['product_id']}.jpg"],
                "price": str(p["price"]),
                "statuses": {"status_description": "Активен", "validation_status": "ok"},
                "price_indexes": {
                    "price_index": "PROFIT",
                    "external_index_data": {"minimal_price": str(p["min_price"])},
                },
                "ozon_index_price": {"minimal_price": str(p["min_price"])},
                "barcodes": p["barcodes"],
                "sources": [{"sku": p["market_sku"]}],
            }
        )
    return {"items": items}


# ---------------------------------------------------------------------------
# Product attributes (v4/product/info/attributes)
# ---------------------------------------------------------------------------

@app.post("/v4/product/info/attributes")
async def product_info_attributes(request: Request):
    body = await request.json()
    offer_ids: list[str] = body.get("filter", {}).get("offer_id") or list(PRODUCTS.keys())
    result = []
    for oid in offer_ids:
        p = PRODUCTS.get(oid)
        if not p:
            continue
        result.append(
            {
                "offer_id": oid,
                "attributes": [
                    {"id": 4191, "values": [{"value": p["description"]}]},
                    {"id": 22336, "values": [{"value": p.get("search_words", "")}]},
                ],
                "height": 50,
                "depth": 100,
                "width": 80,
                "weight": 500,
                "dimension_unit": "mm",
                "weight_unit": "g",
            }
        )
    return {"result": result}


# ---------------------------------------------------------------------------
# Prices (v5/product/info/prices) — used by both price methods
# ---------------------------------------------------------------------------

@app.post("/v5/product/info/prices")
async def product_info_prices(request: Request):
    body = await request.json()
    offer_ids: list[str] = body.get("filter", {}).get("offer_id") or list(PRODUCTS.keys())
    items = []
    for oid in offer_ids:
        p = PRODUCTS.get(oid)
        if not p:
            continue
        items.append(
            {
                "offer_id": oid,
                "product_id": p["product_id"],
                "price": {
                    "price": str(p["price"]),
                    "marketing_price": str(p["marketing_price"]),
                    "marketing_seller_price": str(p["marketing_price"]),
                    "old_price": str(p["old_price"]),
                    "min_price": str(p["min_price"]),
                    "auto_action_enabled": "UNKNOWN",
                    "price_index": "WITHOUT_INDEX",
                    "retail_price": str(p["price"]),
                },
                "commissions": {
                    "sales_percent_fbo": 0.08,
                    "fbo_direct_flow_trans_min_amount": 50.0,
                },
            }
        )
    return {"items": items, "cursor": None, "total": len(items)}


# ---------------------------------------------------------------------------
# Import prices (v1/product/import/prices)
# ---------------------------------------------------------------------------

@app.post("/v1/product/import/prices")
async def import_prices(request: Request):
    body = await request.json()
    result = []
    for item in body.get("prices", []):
        oid = item.get("offer_id")
        if oid and oid in PRODUCTS:
            new_price = item.get("price")
            if new_price is not None:
                PRODUCTS[oid]["price"] = float(new_price)
            new_min = item.get("min_price")
            if new_min is not None:
                PRODUCTS[oid]["min_price"] = float(new_min)
            new_old = item.get("old_price")
            if new_old is not None:
                PRODUCTS[oid]["old_price"] = float(new_old)
        result.append({"offer_id": oid, "updated": True, "errors": []})
    return {"result": result}


# ---------------------------------------------------------------------------
# Import (update offers)  v3/product/import
# ---------------------------------------------------------------------------

@app.post("/v3/product/import")
async def product_import(request: Request):
    body = await request.json()
    for item in body.get("items", []):
        oid = item.get("offer_id")
        if oid and oid in PRODUCTS:
            p = PRODUCTS[oid]
            if item.get("name"):
                p["name"] = item["name"]
            if item.get("description"):
                p["description"] = item["description"]
    task_id = random.randint(100000, 999999)
    return {"result": {"task_id": task_id}}


@app.post("/v1/product/import/info")
async def import_info(request: Request):
    body = await request.json()
    task_id = body.get("task_id", 0)
    return {"result": {"task_id": task_id, "status": "imported", "items": []}}


# ---------------------------------------------------------------------------
# Stocks on warehouses (v2/analytics/stock_on_warehouses)
# ---------------------------------------------------------------------------

@app.post("/v2/analytics/stock_on_warehouses")
async def stock_on_warehouses(request: Request):
    rows = [
        {
            "warehouse_id": 1,
            "warehouse_name": WAREHOUSE_NAME,
            "item_code": sku,
            "item_name": PRODUCTS[sku]["name"],
            "promised_amount": 0,
            "free_to_sell_amount": STOCKS[sku],
            "reserved_amount": 0,
            "sku": PRODUCTS[sku]["market_sku"],
        }
        for sku in PRODUCTS
    ]
    return {"result": {"rows": rows}}


# ---------------------------------------------------------------------------
# Clusters (v1/cluster/list)
# ---------------------------------------------------------------------------

@app.post("/v1/cluster/list")
async def cluster_list():
    return {
        "clusters": [
            {
                "name": "Москва и область",
                "logistic_clusters": [
                    {
                        "warehouses": [
                            {"name": WAREHOUSE_NAME, "type": "FULL_FILLMENT"}
                        ]
                    }
                ],
            }
        ]
    }


# ---------------------------------------------------------------------------
# Content ratings (v1/product/rating-by-sku)
# ---------------------------------------------------------------------------

@app.post("/v1/product/rating-by-sku")
async def rating_by_sku(request: Request):
    body = await request.json()
    skus: list[int] = body.get("skus", [])
    return {
        "products": [
            {"sku": sku, "rating": round(random.uniform(3.5, 5.0), 1)}
            for sku in skus
        ]
    }


# ---------------------------------------------------------------------------
# Orders (v2/posting/fbo/list)
# ---------------------------------------------------------------------------

@app.post("/v2/posting/fbo/list")
async def fbo_orders():
    return {"result": []}


# ---------------------------------------------------------------------------
# Turnover (v1/analytics/turnover/stocks)
# ---------------------------------------------------------------------------

@app.post("/v1/analytics/turnover/stocks")
async def turnover_stocks(request: Request):
    body = await request.json()
    offer_ids: list[str] = body.get("sku", [])
    return {
        "items": [
            {
                "sku": oid,
                "turnover": round(random.uniform(5.0, 90.0), 1),
                "idc": round(random.uniform(1.0, 30.0), 1),
            }
            for oid in offer_ids
        ]
    }
