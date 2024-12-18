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
    const targetPriceFilter = (offer: Offer) => {
        if (!state.attentionMarks.targetPrice.enabled) return true;
        if (offer.current_price === null || offer.target_price === null) return true;
        return offer.current_price !== offer.target_price;
    };
    const stopPriceFilter = (offer: Offer) => {
        if (!state.attentionMarks.stopPrice.enabled) return true;

        let { stop_price, your_promotion_price, current_price, target_price } = offer;
        if (stop_price === null) return false;

        if (your_promotion_price !== null && your_promotion_price < stop_price) return true;
        if (target_price !== null && target_price < stop_price) return true;
        if (current_price !== null && current_price < stop_price) return true;
        return false;
    };

    return (offer: Offer) =>
        searchFilter(offer) &&
        supplierAvailableFilter(offer) &&
        hiddenFilter(offer) &&
        shopFilter(offer) &&
        targetPriceFilter(offer) &&
        stopPriceFilter(offer);
});

export { offersFilter as default };
