import { fetchJSON } from "$lib/fetch";
import { showFetchModals } from "$lib/modal";
import { getStatisticsOnlyOffers, getStatisticsWarehouses } from "./statistics";

export async function fetchFboStorage(
    offer_id: number,
    fetch_?: typeof fetch
): Promise<FboStocks[]> {
    let promise = fetchJSON<FboStocks[]>(`stocks/fbo/offers/${offer_id}`, { fetch: fetch_ });
    let stats = await getStatisticsWarehouses(offer_id);
    showFetchModals(promise.then(x => x.response));
    let data = (await promise).data.map(x => ({
        ...x,
        get statistics() {
            return stats.find(y => y.warehouse_id === x.warehouse_id);
        }
    }));
    return data;
}

export type FboStocks = {
    current_stock: number;
    min_stock: number;
    for_delivery: number;
    can_be_delivered: boolean;
    advice_from_the_store: string;
    in_box: number;
    is_deliver_in_boxes: boolean;
    id: number;
    warehouse_id: number;
};
