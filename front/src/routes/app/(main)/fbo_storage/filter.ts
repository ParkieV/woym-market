import { filterState } from "../state";
import { derived, get } from "svelte/store";
import type { FboStocks, FboStorage } from "$lib/data/fbo_storage";
import createSearchFilter from "$lib/filter/search";
import { fboStocksSelection } from "../selection";

export const fboStorageFilter = derived(filterState, state => {
    const SEARCH_FIELDS = ["sku", "name", "note_1", "note_2", "note_3"] as const;
    let searchFilter = createSearchFilter(state.search, SEARCH_FIELDS);

    return (fboStorage: FboStorage) =>
        searchFilter(fboStorage) &&
        (state.supplierAvailable === null ||
            state.supplierAvailable === fboStorage.supplier_available) &&
        (!fboStorage.hidden || state.showHidden) &&
        state.shops
            .filter(x => x.selected)
            .map(x => x.name)
            .includes(fboStorage.name_of_shop) &&
        state.shops
            .filter(x => x.selected)
            .map(x => x.market)
            .includes(fboStorage.market);
});

export const fboStocksFilter = derived(filterState, state => {
    return (stocks: FboStocks): boolean =>
        !state.hideUnmarkedWarehouses ||
        // When toggle is ON, show only selected rows (both warehouses and clusters)
        (get(fboStocksSelection.selected) as Map<string, FboStocks>).has(
            `${stocks.warehouse.market}:${stocks.warehouse.name}`
        );
});
