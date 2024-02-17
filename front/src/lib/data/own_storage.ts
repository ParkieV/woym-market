import { handleRequest } from "$lib";
import { fetchAuthenticated } from "$lib/auth";
import type { Market } from "./markets";

export type OwnStoragesInfo = {
    markets: Market[];
    data: OwnStorage[];
};

export type OwnStorage = {
    sku: string;
    name: string[];
    photo: (string | null)[];
    note_1: string[];
    note_2: string[];
    note_3: string[];
    name_of_shop: string[];
    market: string[];
    own_storage: {
        id: number;
        value: number;
    };
    stocks: {
        name_of_shop: string;
        market: string;
        value: number;
    }[];
};

export async function fetchOwnStorages(): Promise<OwnStoragesInfo> {
    let promise = fetchAuthenticated("stocks/own-storage");
    let info = await handleRequest(promise, { onSuccess: async response => await response.json() });
    return info as OwnStoragesInfo;
}

export async function patchOwnStorages(storages: OwnStorage[]): Promise<boolean> {
    let data: { id: number; value: number }[] = storages.map(x => {
        return {
            id: x.own_storage.id,
            value: x.own_storage.value
        };
    });

    let promise = fetchAuthenticated("stocks/own-storage", {
        method: "PATCH",
        body: JSON.stringify(data),
        headers: {
            "Content-Type": "application/json"
        }
    });
    let ok = false;
    await handleRequest(promise, { header: "Сохранение...", onSuccess: () => (ok = true) });
    return ok;
}
