import { fetchFboStocks, type FboStocks, type FboStorage } from "$lib/data/fbo_storage";
import { fetchOfferList, type Offer } from "$lib/data/offers";
import { fetchOwnStorages, type OwnStorage } from "$lib/data/own_storage";
import type { Filter } from "$lib/datagrid/filters";
import { ChangeList } from "$lib/datagrid/plugins/changes";
import { Selection } from "$lib/selection";
import { GridState } from "$lib/state";
import { writable } from "svelte/store";

export const offersState = new GridState<Offer, "id">(() => fetchOfferList());
export const offersFilter = writable<Filter<Offer>>(() => true);

export const ownStorageState = new GridState<OwnStorage, "sku">(() =>
    fetchOwnStorages().then(x => x.data)
);
export const ownStorageFilter = writable<Filter<OwnStorage>>(() => true);

export const fboState = new GridState<FboStocks, "id">(() => fetchFboStocks());
export const fboOffersFilter = writable<Filter<FboStocks>>(() => true);
export const fboOffersSelection = new Selection<FboStocks, number>(fboOffersFilter);

export const fboStorageChanges = new ChangeList<FboStorage, "id">();
export const fboStorageFilter = writable<Filter<FboStorage>>(() => true);
export const fboStorageSelection = new Selection<FboStorage, number>(fboStorageFilter);
