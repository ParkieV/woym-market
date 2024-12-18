import type { Offer } from "$lib/data/offers";
import createSearchFilter from "$lib/filter/search";
import { derived } from "svelte/store";
import { filterState } from "../state";
import type { CatalogEntry } from "$lib/data/catalog";

const catalogFilter = derived(filterState, state => {
    const SEARCH_FIELDS = ["sku", "name", "note"] as const;
    const searchFilter = createSearchFilter(state.search, SEARCH_FIELDS);
    const shopFilter = (entry: CatalogEntry) =>
        state.shops
            .filter(x => x.selected)
            .some(({ market, name }) =>
                entry.synchronization.some(x => x.market === market && x.name_of_shop === name)
            );

    return (entry: CatalogEntry) => searchFilter(entry) && shopFilter(entry);
});

export { catalogFilter as default };
