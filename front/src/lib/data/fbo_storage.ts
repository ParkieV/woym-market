import { fetchJSON, fetchPlain } from "$lib/fetch";
import { showFetchModals } from "$lib/modal";
import type { FboStocks } from "./fbo_stocks";
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

export async function fetchFboStorage(fetch_?: typeof fetch): Promise<FboStorage[]> {
    let promise = fetchJSON<FboStorage[]>("stocks/fbo", { fetch: fetch_, method: "POST" });
    showFetchModals(promise.then(x => x.response));
    let data = (await promise).data;
    return data;
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
