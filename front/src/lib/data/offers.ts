import { BaseUrl } from "$lib";
import { fetchAuthenticated } from "$lib/auth";

/** Class that manages list of offers. */
export class OffersData {
    private _offers: Offer[];

    /** Datetime when offer list was last updated from remote. */
    public updated_at: Date | null = null;

    constructor() {
        this._offers = [];
    }

    /** Returns current list of offers. */
    public get offers(): Offer[] {
        return this._offers;
    }

    /** Updates data from remote. */
    public async update() {
        let data = await fetchOfferList();
        this._offers.splice(0, this._offers.length, ...data);
    }
}

/** Product in store. */
export type Offer = {
    sku: string;
    name: string;
    photo?: string | null;
    note_1?: string | null;
    note_2?: string | null;
    note_3?: string | null;

    self_weight: number;
    self_length: number;
    self_width: number;
    self_height: number;

    yandex_weight: number;
    yandex_length: number;
    yandex_width: number;
    yandex_height: number;

    volume: number;
    yandex_volume: number;
    volumn_difference: number | null;

    name_of_shop: string;
    market: string;
    group_sellers_amount: number;
    business_id: number;

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
    hidden: boolean;
};

type OfferPatch = { sku: string } & Partial<Offer>;

export async function fetchOfferList(): Promise<Offer[]> {
    let offers = await (await fetchAuthenticated("data/offers")).json();
    return offers;
}

export async function patchOfferList(changed: Offer[]): Promise<void> {
    for (const offer of changed) {
        // Backend doesn't handle null values well, replace them with empty string before patching.
        offer.note_1 = offer.note_1 ? offer.note_1 : "";
        offer.note_2 = offer.note_2 ? offer.note_2 : "";
        offer.note_3 = offer.note_3 ? offer.note_3 : "";
    }

    await fetchAuthenticated("data/offers", {
        method: "PATCH",
        body: JSON.stringify(changed),
        headers: {
            "Content-Type": "application/json"
        }
    });
}
