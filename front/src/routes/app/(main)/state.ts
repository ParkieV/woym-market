import { ChangeList } from "$lib/datagrid/plugins/changes";
import Filter from "$lib/filter";
import { GridState } from "$lib/state";

import { fetchOfferList, type Offer } from "$lib/data/offers";
import { fetchCatalog, type CatalogEntry } from "$lib/data/catalog";
import { fetchOwnStorages, type OwnStorage } from "$lib/data/own_storage";
import { fetchFboStorage, type FboStorage, type FboStorageFull } from "$lib/data/fbo_storage";
import type { FboStocks } from "$lib/data/fbo_stocks";
import { Cache } from "$lib/cache";
import { getWarehouses } from "$lib/data/warehouse";
import {
    getStatisticsOnlyOffers,
    getStatisticsWarehouses,
    type Statistics
} from "$lib/data/statistics";

export const filterState = new Filter();

export const offersState = new GridState<Offer, number>(() => fetchOfferList());
export const catalogState = new GridState<CatalogEntry, string>(() => fetchCatalog());
export const ownStorageState = new GridState<OwnStorage, string>(() => fetchOwnStorages());
export const fboState = new GridState<FboStorageFull, number>(async () => {
    let [offers, fboStorage, stats] = await Promise.all([
        fetchOfferList(),
        fetchFboStorage(),
        getStatisticsOnlyOffers()
    ]);
    return offers.map(offer => ({
        ...offer,
        ...fboStorage.find(fbo => fbo.id === offer.id)!,
        get statistics() {
            return stats.find(x => x.offer_id === offer.id)!;
        }
    }));
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
