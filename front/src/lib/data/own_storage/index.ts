import { fetchJSON, fetchPlain } from "$lib/fetch";
import { showFetchModals } from "$lib/modal";

export type OwnStorage = {
    offer: {
        sku: string;
        name: (string | null)[];
        photo: (string | null)[];
        note_1: (string | null)[];
        note_2: (string | null)[];
        note_3: (string | null)[];
        barcodes: (string | null)[];
        market: string[];
        name_of_shop: string[];
    };
    storages: [
        {
            id: number;
            sku: string;
            value: number;
            storage_place_id: number;
        }
    ];
    stocks: [
        {
            sku: string;
            name_of_shop: string;
            market: string;
            stock: number;
        }
    ];
};

type UpdateOwnStorage = { id: number; value: number; storage_place_id: number };

export async function fetchOwnStorages(): Promise<OwnStorage[]> {
    let promise = fetchJSON<OwnStorage[]>("/stocks/own-storage");
    showFetchModals(promise.then(x => x.response));
    return (await promise).data;
}

export async function patchOwnStorages(storages: OwnStorage[]): Promise<boolean> {
    let data: UpdateOwnStorage[] = storages.flatMap(x => x.storages);
    let promise = fetchPlain("/stocks/own-storage", {
        method: "PATCH",
        body: JSON.stringify(data),
        headers: {
            "Content-Type": "application/json"
        }
    });
    showFetchModals(promise, "Сохранение...");
    return (await promise).ok;
}
