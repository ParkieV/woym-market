import { fetchAuthenticated } from "./auth";
import { PUBLIC_BASE_URL } from "$env/static/public";

export const BaseUrl = PUBLIC_BASE_URL;

// TODO: Improve documentation
export type Offer = {
    sku: string;
    /** URL to the photo of the product */
    photo?: string | null;
    /** Name of the product. */
    name: string;
    note_1?: string | null;
    note_2?: string | null;
    note_3?: string | null;
    /** Weight of the product. */
    weight: number;
    /** Length of the product. */
    length: number;
    /** Width of the product. */
    width: number;
    /** Height of the product. */
    height: number;

    /** Final price calculated by service. */
    total_price: number;
    /** Price that is currently set in Yandex Market. */
    current_price: number | null;
    /** Price after calculations. */
    target_price: number | null;
    /** The price **in rubles** at which goods are or have been bought by a merchant or retailer. */
    cost_price: number;
    /** The price **in dollars** at which goods are or have been bought by a merchant or retailer. */
    dollar_cost_price: number;
    /** Minimal addition to the total price. */
    total_price_min_additional: number;

    total_price_coeff: number;
    discount_base_price: number | null;
    profit: number | null;
    margin: number | null;
    fby: number | null;
    minimum_group_price: number;
    name_of_shop: string;
    remaining_stock: number;
    auto_min_price: number;
    manual_min_price: number | null;

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
    let offers = await (await fetch(BaseUrl + "offers")).json();
    return offers;
}

export async function patchOfferList(changed: Offer[]): Promise<void> {
    for (const offer of changed) {
        // Backend doesn't handle null values well, replace them with empty string before patching.
        offer.note_1 = offer.note_1 ? offer.note_1 : "";
        offer.note_2 = offer.note_2 ? offer.note_2 : "";
        offer.note_3 = offer.note_3 ? offer.note_3 : "";
    }

    await fetchAuthenticated("offers", {
        method: "PATCH",
        body: JSON.stringify(changed),
        headers: {
            "Content-Type": "application/json"
        }
    });
}

export async function fetchLogs(): Promise<{ updated_at: string | null }> {
    return await (await fetchAuthenticated("offers/logs")).json();
}
