import { fetchJSON, fetchPlain } from "$lib/fetch";
import { showFetchModals } from "$lib/modal";
import type { OfferBase } from "./offers";

export type FboStorage = OfferBase & {
    stocks: FboStocks[];
    name_of_shop: string;
    supplier_available: boolean;
    volume: number;
    margin: number;
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
        name: string;
        warehouse_type: "warehouse" | "cluster";
    };
    in_box: number;
    is_deliver_in_boxes: number;
};

export async function fetchFboStorage(fetch_?: typeof fetch): Promise<FboStorage[]> {
    let promise = fetchJSON<FboStorage[]>("stocks/fbo", { fetch: fetch_ });
    showFetchModals(promise.then(x => x.response));
    return (await promise).data;
}

export async function patchFboStorage(changed: FboStorage[]): Promise<boolean> {
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
