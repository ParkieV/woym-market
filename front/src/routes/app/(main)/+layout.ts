import { getStores } from "$lib/data/markets";
import type { LayoutLoad } from "./$types";
import { getStoragePlaces } from "$lib/data/own_storage/places";
import { getWarehouses } from "$lib/data/warehouse";

export const load: LayoutLoad = async ({ fetch }) => {
    let [markets, storages, warehouses] = await Promise.all([
        getStores({ fetch }),
        getStoragePlaces({ fetch }),
        getWarehouses({ fetch })
    ]);
    return { markets, storages, warehouses };
};
