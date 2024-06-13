import { fetchJSON, fetchPlain } from "$lib/fetch";
import { showFetchModals } from "$lib/modal";
import type { OfferBase } from "./offers";

export type FboStocks = OfferBase & {
    stocks: FboStorage[];
    name_of_shop: string;
    supplier_available: boolean;
    hidden: boolean;
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
