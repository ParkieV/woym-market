import { fetchJSON, fetchPlain } from "$lib/fetch";
import { showFetchModals } from "$lib/modal";
import type { OfferBase } from "./offers";

export type FboStocks = OfferBase & {
    stocks: FboStorage[];
};

export type FboStorage = {
    id: number;
    current_stock: number;
    min_stock: number;
    warehouse: {
        id: number;
        name: string;
    };
};

export async function fetchFboStocks(): Promise<FboStocks[]> {
    let promise = fetchJSON<FboStocks[]>("stocks/fbo");
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
