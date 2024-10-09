import { fetchJSON } from "$lib/fetch";
import { showFetchModals } from "$lib/modal";

export async function getStatisticsOnlyOffers() {
    let promise = fetchJSON<Statistics[]>(`orders/statistic/only-offers`, {
        method: "POST",
        body: JSON.stringify({ warehouse_ids: [], offer_ids: [] })
    });
    showFetchModals(promise.then(x => x.response));
    return (await promise).data;
}

export async function getStatisticsWarehouses() {
    let promise = fetchJSON<(Statistics & { warehouse_id: number })[]>(
        `orders/statistic/offers-with-warehouses`,
        { method: "POST" }
    );
    showFetchModals(promise.then(x => x.response));
    let data = (await promise).data;
    return data;
}

type Statistics = {
    offer_id: number;
    today: number;
    yesterday: number;
    for_7_days: number;
    for_14_days: number;
    for_28_days: number;
    for_60_days: number;
    for_120_days: number;
    smart_delivery: number;
};
