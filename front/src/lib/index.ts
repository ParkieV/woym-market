import { fetchAuthenticated } from "./auth";
import { PUBLIC_BASE_URL } from "$env/static/public";

export const BaseUrl = PUBLIC_BASE_URL;

// TODO: Improve documentation
export type Offer = {
    id: number;
    sku: string;
    /** URL to the photo of the product */
    photo?: string;
    /** Name of the product. */
    name: string;
    note_1?: string;
    note_2?: string;
    note_3?: string;
    /** Weight of the product. */
    weight: number;
    /** Length of the product. */
    length: number;
    /** Width of the product. */
    width: number;
    /** Height of the product. */
    height: number;
    /** Volume that is provided by Yandex (may differ from self-calculated one). */
    volume_yandex: number;

    /** Final price calculated by service. */
    total_price: number;
    /** Price that is currently set in Yandex Market. */
    current_price?: number;
    /** The price **in rubles** at which goods are or have been bought by a merchant or retailer. */
    cost_price: number;
    /** The price **in dollars** at which goods are or have been bought by a merchant or retailer. */
    dollar_cost_price: number;
    /** Minimal addition to the total price. */
    total_price_min_additional: number;

    total_price_coeff: number;
    discount_base_price: number;
    profit: number;
    payback: number;
    fby: number;
    minimum_group_price: number;
    group_sellers_amount: number;
    name_of_shop: string;
    remaining_stock: number;

    /** Sets if automatic control of the current price is enabled. */
    auto_price_control: boolean;
    /** If set to true, manual min price (manual_min_price) will be used. */
    use_manual_min_price: boolean;
};

export async function patchUserInfo(val: { rate: number }): Promise<void> {
    let init: RequestInit = {
        method: "PATCH",
        body: JSON.stringify(val),
        headers: {
            "Content-Type": "application/json"
        }
    };
    await fetchAuthenticated("users/settings", init);
}

export async function fetchUserInfo(): Promise<{ rate: number }> {
    let info = await (await fetchAuthenticated("users/settings")).json();
    return info;
}

export async function fetchOfferList(): Promise<Offer[]> {
    let offers = await (await fetch("http://5.35.88.225:8000/offers/")).json();
    return offers;
}
