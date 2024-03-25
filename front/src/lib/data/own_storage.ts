import { fetchJSON, fetchPlain } from "$lib/fetch";
import { showFetchModals } from "$lib/modal";
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
    let promise = fetchJSON<OwnStoragesInfo>("stocks/own-storage");
    showFetchModals(promise.then(x => x.response));
    return (await promise).data;
}

export async function patchOwnStorages(storages: OwnStorage[]): Promise<boolean> {
    let data: { id: number; value: number }[] = storages.map(x => {
        return {
            id: x.own_storage.id,
            value: x.own_storage.value
        };
    });
    let promise = fetchPlain("stocks/own-storage", {
        method: "PATCH",
        body: JSON.stringify(data),
        headers: {
            "Content-Type": "application/json"
        }
    });
    showFetchModals(promise, "Сохранение...");
    return (await promise).ok;
}
