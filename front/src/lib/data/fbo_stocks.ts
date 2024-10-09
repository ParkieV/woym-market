import { fetchJSON } from "$lib/fetch";
import { showFetchModals } from "$lib/modal";

export async function fetchFboStorage(
    offer_id: number,
    fetch_?: typeof fetch
): Promise<FboStocks[]> {
    let promise = fetchJSON<FboStocks[]>(`stocks/fbo/offers/${offer_id}`, { fetch: fetch_ });
    showFetchModals(promise.then(x => x.response));
    let data = (await promise).data;
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
};
