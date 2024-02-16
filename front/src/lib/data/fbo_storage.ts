import { handleRequest } from "$lib";
import { fetchAuthenticated } from "$lib/auth";
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
    let promise = fetchAuthenticated("stocks/fbo");
    await handleRequest(promise);
    return await (await promise).json();
}

export async function patchFboStocks(changed: FboStocks[]): Promise<boolean> {
    let promise = fetchAuthenticated("stocks/fbo", {
        method: "PATCH",
        body: JSON.stringify(changed),
        headers: {
            "Content-Type": "application/json"
        }
    });
    let ok = false;
    await handleRequest(promise, { header: "Сохранение...", onSuccess: () => (ok = true) });
    return ok;
}
