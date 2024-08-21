import { ChangeList } from "$lib/datagrid/plugins/changes";
import Filter from "$lib/filter";
import { GridState } from "$lib/state";

import { fetchOfferList, type Offer } from "$lib/data/offers";
import { fetchCatalog, type CatalogEntry } from "$lib/data/catalog";
import { fetchOwnStorages, type OwnStorage } from "$lib/data/own_storage";
import { fetchFboStorage, type FboStorage, type FboStocks } from "$lib/data/fbo_storage";

export const filterState = new Filter();

export const offersState = new GridState<Offer, number>(() => fetchOfferList());
export const catalogState = new GridState<CatalogEntry, string>(() => fetchCatalog());
export const ownStorageState = new GridState<OwnStorage, string>(() => fetchOwnStorages());
export const fboState = new GridState<FboStorage, number>(() => fetchFboStorage());
export const fboStocksChanges = new ChangeList<FboStocks, number>();

export async function invalidateAllState() {
    Promise.all([offersState.reset(), ownStorageState.reset(), fboState.reset()]);
    fboStocksChanges.clear();
}
