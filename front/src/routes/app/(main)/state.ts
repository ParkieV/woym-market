import { ChangeList } from "$lib/datagrid/plugins/changes";
import Filter from "$lib/filter";
import { GridState } from "$lib/state";

import { fetchOfferList, type Offer } from "$lib/data/offers";
import { fetchCatalog, type CatalogEntry } from "$lib/data/catalog";
import { fetchOwnStorages, type OwnStorage } from "$lib/data/own_storage";
import { fetchFboStorage, type FboStorage } from "$lib/data/fbo_storage";
import type { FboStocks } from "$lib/data/fbo_stocks";
import { Cache } from "$lib/cache";
import { getWarehouses } from "$lib/data/warehouse";

export const filterState = new Filter();

export const offersState = new GridState<Offer, number>(() => fetchOfferList());
export const catalogState = new GridState<CatalogEntry, string>(() => fetchCatalog());
export const ownStorageState = new GridState<OwnStorage, string>(() => fetchOwnStorages());
export const fboState = new GridState<any, number>(async () => {
    let [offers, fboStorage] = await Promise.all([fetchOfferList(), fetchFboStorage()]);
    console.log(offers[0], fboStorage[0]);
    // offers.map)
    return offers;
});
export const fboStocksChanges = new ChangeList<FboStocks, number>();
export const warehouses = new Cache(() => getWarehouses());

export async function invalidateAllState() {
    Promise.all([
        offersState.reset(),
        catalogState.reset(),
        ownStorageState.reset(),
        fboState.reset()
    ]);
    fboStocksChanges.clear();
}
