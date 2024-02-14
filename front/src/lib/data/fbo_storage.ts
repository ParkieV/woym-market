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
    return await (await fetchAuthenticated("stocks/fbo")).json();
}

export async function patchFboStocks(changed: FboStocks[]) {
    await fetchAuthenticated("stocks/fbo", {
        method: "PATCH",
        body: JSON.stringify(changed),
        headers: {
            "Content-Type": "application/json"
        }
    });
}
