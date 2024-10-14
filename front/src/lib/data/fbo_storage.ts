import { fetchJSON, fetchPlain } from "$lib/fetch";
import { showFetchModals } from "$lib/modal";
import type { FboStocks } from "./fbo_stocks";
import type { Offer, OfferBase } from "./offers";
import { getStatisticsOnlyOffers, type Statistics } from "./statistics";

export type FboStorage = {
    name_of_shop: string;
    supplier_available: boolean;
    volume: number;
    margin: number;
    self_weight: number;
    cost_price: number;
    profit: number;
};

export type FboStorageFull = Offer & FboStorage & { statistics: Statistics };

export async function fetchFboStorage(fetch_?: typeof fetch): Promise<FboStorage[]> {
    let promise = fetchJSON<FboStorageFull[]>("stocks/fbo", { fetch: fetch_, method: "POST" });
    let stats = await getStatisticsOnlyOffers();
    showFetchModals(promise.then(x => x.response));
    let data = (await promise).data.map(x => ({
        ...x,
        get statistics() {
            return { for_120_days: 5 };
            console.log(stats);
            return stats.find(y => y.offer_id === x.id);
        }
    }));
    return data;
}

export async function patchFboStorage(changed: FboStorage[]): Promise<boolean> {
    let promise = fetchPlain("stocks/fbo", {
        method: "PATCH",
        body: JSON.stringify(changed),
        headers: {
            "Content-Type": "application/json"
        }
    });
    showFetchModals(promise, "Сохранение...");
    return (await promise).ok;
}
