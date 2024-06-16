import { fetchJSON, fetchPlain } from "$lib/fetch";
import { showFetchModals } from "$lib/modal";
import type { OfferBase } from "./offers";

export type FboStocks = OfferBase & {
    stocks: FboStorage[];
    name_of_shop: string;
    supplier_available: boolean;
    volume: number;
    margin: number;
    self_weight: number;
    cost_price: number;
    profit: number;
};

export type FboStorage = {
    id: number;
    current_stock: number;
    min_stock: number;
    warehouse: {
        id: number;
        name: string;
        warehouse_type: "warehouse" | "cluster";
    };
    in_box: number;
    is_deliver_in_boxes: number;
};

export async function fetchFboStocks(fetch_?: typeof fetch): Promise<FboStocks[]> {
    let promise = fetchJSON<FboStocks[]>("stocks/fbo", { fetch: fetch_ });
    showFetchModals(promise.then(x => x.response));
    return (await promise).data;
}

export async function patchFboStocks(changed: FboStocks[]): Promise<boolean> {
    let promise = fetchPlain("stocks/fbo", {
        method: "PATCH",
        body: JSON.stringify(changed),
        headers: {
            "Content-Type": "application/json"
        }
    });
    showFetchModals(promise, "Сохранение...");
    return (await promise).ok;
}
