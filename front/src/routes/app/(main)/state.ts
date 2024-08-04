import { fetchFboStocks, type FboStocks, type FboStorage } from "$lib/data/fbo_storage";
import { fetchOfferList, type Offer } from "$lib/data/offers";
import { fetchOwnStorages, type OwnStorage } from "$lib/data/own_storage";
import type { Filter } from "$lib/datagrid/filters";
import { ChangeList } from "$lib/datagrid/plugins/changes";
import { Selection } from "$lib/selection";
import { GridState } from "$lib/state";
import { writable } from "svelte/store";

export const offersState = new GridState<Offer, number>(() => fetchOfferList());
export const offersFilter = writable<Filter<Offer>>(() => true);

export const ownStorageState = new GridState<OwnStorage, string>(() => fetchOwnStorages());
export const ownStorageFilter = writable<Filter<OwnStorage>>(() => true);

export const fboState = new GridState<FboStocks, number>(() => fetchFboStocks());
export const fboOffersFilter = writable<Filter<FboStocks>>(() => true);
export const fboOffersSelection = new Selection<FboStocks, number>(fboOffersFilter);

export const fboStorageChanges = new ChangeList<FboStorage, number>();
export const fboStorageFilter = writable<Filter<FboStorage>>(() => true);
export const fboStorageSelection = new Selection<FboStorage, number>(fboStorageFilter);

export async function invalidateAllState() {
    Promise.all([offersState.reset(), ownStorageState.reset(), fboState.reset()]);

    let filter = () => true;
    offersFilter.set(filter);
    ownStorageFilter.set(filter);
    fboOffersFilter.set(filter);
    fboStorageFilter.set(filter);

    fboOffersSelection.clear();
    fboStorageSelection.clear();
    fboStorageChanges.clear();
}
