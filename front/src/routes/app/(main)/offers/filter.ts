import type { Offer } from "$lib/data/offers";
import createSearchFilter from "$lib/filter/search";
import { derived } from "svelte/store";
import { filterState } from "../state";

const offersFilter = derived(filterState, state => {
    const SEARCH_FIELDS = ["sku", "name", "note_1", "note_2", "note_3"] as const;
    const searchFilter = createSearchFilter(state.search, SEARCH_FIELDS);
    const supplierAvailableFilter = (offer: Offer) =>
        state.supplierAvailable === null || state.supplierAvailable === offer.supplier_available;
    const hiddenFilter = (offer: Offer) => !offer.hidden || state.showHidden;
    const shopFilter = (offer: Offer) =>
        state.shops
            .filter(x => x.selected)
            .some(({ market, name }) => market === offer.market && name === offer.name_of_shop);

    return (offer: Offer) =>
        searchFilter(offer) &&
        supplierAvailableFilter(offer) &&
        hiddenFilter(offer) &&
        shopFilter(offer);
});

export { offersFilter as default };
