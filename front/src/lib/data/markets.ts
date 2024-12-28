import { fetchJSON, fetchPlain, type FetchInit } from "$lib/fetch";
import { showFetchModals } from "$lib/modal";
import { filterUnique } from "$lib/util";

export type Market = {
    id: number;
    name: string;
    type: string;

    /** Налог */
    tax: number;
    /** Текущий курс */
    rate: number;
    /** Комиссия за продажу FBO (%) */
    fbo_sales_commission: number;

    /** Параметр формулы РРЦ, "Число 1" */
    first_variable_for_recommended_retail_price: number;
    /** Параметр формулы РРЦ, "Число 2" */
    second_variable_for_recommended_retail_price: number;

    /** Параметр формулы стоп-цены, "Число 1" */
    first_variable_for_stop_price: number;
    /** Параметр формулы стоп-цены, "Число 2" */
    second_variable_for_stop_price: number;

    /** Скидка на товары */
    discount_purchase: number;
    /** Цена до скидки (%) */
    price_before_discount: number;

    /** Цена долгосрочного хранения */
    long_term_storage_cost: number;
    /** Порог для дополнительной логистики за 1 литр */
    volume_threshold_for_additional_logistics: number;
    /** Цена дополнительной логистики за 1 литр */
    cost_of_additional_logistics_per_liter: number;
};

export async function getStores(init?: FetchInit): Promise<Market[]> {
    const promise = fetchJSON<Market[]>("/settings/markets", init);
    showFetchModals(
        promise.then(x => x.response),
        undefined,
        "Не удалось получить список магазинов"
    );
    return (await promise).data;
}

export async function patchStore(store: Market) {
    console.log('Market response', store);
    const promise = fetchPlain(`/settings/markets/${store.id}`, {
        method: "PATCH",
        body: JSON.stringify(store),
        headers: {
            "Content-Type": "application/json"
        }
    });
    showFetchModals(promise, "Сохранение...");
    await promise;
}

export async function getStoreNames(type?: string): Promise<string[]> {
    const stores = await getStores();
    return stores
        .filter(x => type === undefined || x.type === type)
        .map(x => x.name)
        .filter(filterUnique);
}

export async function getStoreTypes(): Promise<string[]> {
    const stores = await getStores();
    return stores.map(x => x.type).filter(filterUnique);
}
