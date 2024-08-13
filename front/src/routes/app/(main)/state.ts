import { fetchFboStorage, type FboStorage, type FboStocks } from "$lib/data/fbo_storage";
import { fetchOfferList, type Offer } from "$lib/data/offers";
import { fetchOwnStorages, type OwnStorage } from "$lib/data/own_storage";
import { ChangeList } from "$lib/datagrid/plugins/changes";
import Filter from "$lib/filter";
import { Selection } from "$lib/selection";
import { GridState } from "$lib/state";
import { getOffersFilter } from "./(offers)/Toolbar.svelte";
import { getFboStorageFilter, getFboStocksFilter } from "./fbo_storage/Toolbar.svelte";
import { getOwnStorageFilter } from "./own_storage/Toolbar.svelte";

export const filterState = new Filter();

export const offersState = new GridState<Offer, number>(() => fetchOfferList());
export const offersFilter = getOffersFilter();

export const ownStorageState = new GridState<OwnStorage, string>(() => fetchOwnStorages());
export const ownStorageFilter = getOwnStorageFilter();

export const fboState = new GridState<FboStorage, number>(() => fetchFboStorage());
export const fboStorageFilter = getFboStorageFilter();
export const fboStorageSelection = new Selection<FboStorage, number>(fboStorageFilter);

export const fboStocksChanges = new ChangeList<FboStocks, number>();
export const fboStocksFilter = getFboStocksFilter();
export const fboStocksSelection = new Selection<FboStocks, number>(fboStocksFilter);

export async function invalidateAllState() {
    Promise.all([offersState.reset(), ownStorageState.reset(), fboState.reset()]);

    fboStorageSelection.clear();
    fboStocksSelection.clear();
    fboStocksChanges.clear();
}
