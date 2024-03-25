import { fetchJSON, fetchPlain } from "$lib/fetch";
import { showFetchModals } from "$lib/modal";

/** Basic information about the offer. */
export type OfferBase = {
    id: number;
    sku: string;
    name: string;
    photo: string | null;
    note_1: string | null;
    note_2: string | null;
    note_3: string | null;
    name_of_shop: string;
    market: string;
    hidden: boolean;
};

/** Product in store. */
export type Offer = OfferBase & {
    self_weight: number | null;
    self_length: number | null;
    self_width: number | null;
    self_height: number | null;
    volume: number | null;

    yandex_weight: number | null;
    yandex_length: number | null;
    yandex_width: number | null;
    yandex_height: number | null;
    yandex_volume: number | null;

    volumn_difference: number | null;

    group_sellers_amount: number;
    business_id: number;

    /** Final price calculated by service. */
    total_price: number | null;
    /** Price that is currently set in Yandex Market. */
    current_price: number | null;
    /** Price after calculations. */
    target_price: number | null;
    /** The price **in rubles** at which goods are or have been bought by a merchant or retailer. */
    cost_price: number | null;
    /** The price **in dollars** at which goods are or have been bought by a merchant or retailer. */
    dollar_cost_price: number | null;
    /** Minimal addition to the total price. */
    total_price_min_additional: number;

    total_price_coeff: number;
    discount_base_price: number | null;
    profit: number | null;
    margin: number | null;
    fbo: number | null;
    minimum_group_price: number;
    remaining_stock: number;
    auto_min_price: number;
    manual_min_price: number | null;

    attractive_price_threshold: number;
    moderately_attractive_price_threshold: number;

    best_place_wm: string;
    best_price_wm: number;
    best_place_im: string;
    best_price_im: number;

    /** Sets if automatic control of the current price is enabled. */
    auto_price_control: boolean;
    /** If set to true, manual min price (manual_min_price) will be used. */
    use_manual_min_price: boolean;
};

export async function fetchOfferList(): Promise<Offer[]> {
    let offers = fetchJSON<Offer[]>("data/offers");
    showFetchModals(offers.then(x => x.response));
    return (await offers).data;
}

export async function patchOfferList(changed: Offer[]): Promise<boolean> {
    let response = fetchPlain("data/offers", {
        method: "PATCH",
        body: JSON.stringify(changed),
        headers: {
            "Content-Type": "application/json"
        }
    });
    showFetchModals(response, "Сохранение...");
    return (await response).ok;
}
