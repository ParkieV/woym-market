import { handleRequest } from "$lib";
import { fetchAuthenticated } from "$lib/auth";
import { filterUnique } from "$lib/util";

export type Market = {
    id: number;
    name: string;
    type: string;
    tax: number;
};

export async function getStores(): Promise<Market[]> {
    let promise = fetchAuthenticated("settings/markets");
    let markets = await handleRequest(promise, {
        errorHeader: "Не удалось получить список магазинов",
        onSuccess: async response => {
            return (await response.json()) as Market[];
        }
    });
    return markets!;
}

export async function getStoreNames(): Promise<string[]> {
    let stores = await getStores();
    return stores.map(x => x.name).filter(filterUnique);
}

export async function getStoreTypes(): Promise<string[]> {
    let stores = await getStores();
    return stores.map(x => x.type).filter(filterUnique);
}
