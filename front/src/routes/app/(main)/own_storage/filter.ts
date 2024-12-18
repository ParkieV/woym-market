import type { OwnStorage } from "$lib/data/own_storage";
import createSearchFilter from "$lib/filter/search";
import { derived } from "svelte/store";
import { filterState } from "../state";

const ownStorageFilter = derived(filterState, state => {
    const FIELDS = ["name", "note_1", "note_2", "note_3"] as const;
    const sku = (data: OwnStorage) => data.offer.sku;
    const getters = FIELDS.map(field => (data: OwnStorage) => data.offer[field].map(x => x ?? ""));
    let searchFilter = createSearchFilter(state.search, [sku, ...getters]);

    return (storage: OwnStorage) =>
        searchFilter(storage) &&
        storage.offer.name_of_shop.some(shop =>
            state.shops
                .filter(x => x.selected)
                .map(x => x.name)
                .includes(shop)
        );
});

export { ownStorageFilter as default };
