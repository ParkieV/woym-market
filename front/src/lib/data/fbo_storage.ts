import {type FetchInit, fetchJSON, fetchPlain} from "$lib/fetch";
import { showFetchModals } from "$lib/modal";
import type { OfferBase } from "./offers";

export type FboStorage = OfferBase & {
    stocks: FboStocks[];
    name_of_shop: string;
    supplier_available: boolean;
    volume: number;
    margin: number;
    min_stock: number;
    self_weight: number;
    cost_price: number;
    profit: number;
};

export type FboStocks = {
    id: number;
    current_stock: number;
    min_stock: number;
    warehouse: {
        id: number;
        market: string;
        name: string;
        warehouse_type: "warehouse" | "cluster";
    };
    in_box: number;
    is_deliver_in_boxes: number;
};

export async function fetchFboStorage(fetch_?: FetchInit): Promise<FboStorage[]> {
    if (fetch_) {
        fetch_.method = "POST";
    } else {
        fetch_ = {
            method: "POST",
            headers: {"Content-Type": "application/json"},
        }
    }

    let promise = fetchJSON<FboStorage[]>("/stocks/fbo", fetch_);
    showFetchModals(promise.then(x => x.response));
    let data = (await promise).data;

    data.forEach(({ stocks }) =>
        stocks.sort(({ warehouse: a }, { warehouse: b }) => {
            if (a.warehouse_type === b.warehouse_type) {
                return a.name.localeCompare(b.name);
            } else if (a.warehouse_type === "cluster") {
                return -1;
            } else {
                return 1;
            }
        })
    );
    return data;
}

export async function patchFboStocks(changed: FboStocks[]): Promise<boolean> {
    const promise = fetchPlain("/stocks/fbo", {
        method: "PATCH",
        body: JSON.stringify(changed),
        headers: {
            "Content-Type": "application/json"
        }
    });
    showFetchModals(promise, "Сохранение...");
    return (await promise).ok;
}

export async function patchFboStocksOffers(changed: FboStorage[]): Promise<boolean> {
    const body = {
        offers: changed
    }
    console.log(body)
    const promise = fetchPlain('/v2/offers/fbo-stocks', {
        method: "PATCH",
        body: JSON.stringify(body),
        headers: {
            "Content-Type": "application/json"
        }
    });
    showFetchModals(promise, "Сохранение...");
    return (await promise).ok;
}
