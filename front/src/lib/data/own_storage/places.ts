import { fetchJSON, type FetchInit } from "$lib/fetch";
import { showFetchModals } from "$lib/modal";

export async function getStoragePlaces(init?: FetchInit): Promise<StoragePlace[]> {
    let promise = fetchJSON<StoragePlace[]>("/stocks/own-storage/places", init);
    showFetchModals(
        promise.then(x => x.response),
        undefined,
        "Не удалось получить список складов"
    );
    return (await promise).data;
}

export type StoragePlace = {
    id: number;
    name: string;
};
