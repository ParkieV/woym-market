import { fetchFboStorage, type FboStorage, type FboStocks } from "$lib/data/fbo_storage";
import { fetchOfferList, type Offer } from "$lib/data/offers";
import { fetchOwnStorages, type OwnStorage } from "$lib/data/own_storage";
import { ChangeList } from "$lib/datagrid/plugins/changes";
import Filter from "$lib/filter";
import { GridState } from "$lib/state";

export const filterState = new Filter();

export const offersState = new GridState<Offer, number>(() => fetchOfferList());

export const ownStorageState = new GridState<OwnStorage, string>(() => fetchOwnStorages());

export const fboState = new GridState<FboStorage, number>(() => fetchFboStorage());

export const fboStocksChanges = new ChangeList<FboStocks, number>();

export async function invalidateAllState() {
    Promise.all([offersState.reset(), ownStorageState.reset(), fboState.reset()]);
    fboStocksChanges.clear();
}
