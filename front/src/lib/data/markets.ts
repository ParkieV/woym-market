import { fetchJSON, type FetchInit } from "$lib/fetch";
import { showFetchModals } from "$lib/modal";
import { filterUnique } from "$lib/util";

export type Market = {
    id: number;
    name: string;
    type: string;
    tax: number;
    long_term_storage_cost: number;
};

export async function getStores(init?: FetchInit): Promise<Market[]> {
    let promise = fetchJSON<Market[]>("settings/markets", init);
    showFetchModals(
        promise.then(x => x.response),
        undefined,
        "Не удалось получить список магазинов"
    );
    return (await promise).data;
}

export async function getStoreNames(): Promise<string[]> {
    let stores = await getStores();
    return stores.map(x => x.name).filter(filterUnique);
}

export async function getStoreTypes(): Promise<string[]> {
    let stores = await getStores();
    return stores.map(x => x.type).filter(filterUnique);
}
