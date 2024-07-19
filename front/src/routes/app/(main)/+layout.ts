import { getStores } from "$lib/data/markets";
import type { LayoutLoad } from "./$types";
import { getStoragePlaces } from "$lib/data/own_storage/places";

export const load: LayoutLoad = async ({ fetch }) => {
    let [markets, storages] = await Promise.all([
        getStores({ fetch }),
        getStoragePlaces({ fetch })
    ]);
    return {
        markets,
        storages
    };
};
