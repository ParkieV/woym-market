import { fetchJSON, fetchPlain } from "$lib/fetch";
import { showFetchModals } from "$lib/modal";

export type CatalogEntry = {
    sku: string;
    name: string;
    description: string;
    barcodes: string;
    search_words: string;
    note: string;

    self_weight: number | null;
    self_length: number | null;
    self_width: number | null;
    self_height: number | null;
    volume: number | null;
    use_promotion_price: boolean;
    wholesale_dollar_cost_price: number;
    synchronization: Synchronization[];
};

export type Synchronization = {
    id: number;
    sku: string;
    market: string;
    name_of_shop: string;
    synchronization: boolean;
};

export async function fetchCatalog(): Promise<CatalogEntry[]> {
    let offers = fetchJSON<CatalogEntry[]>("/catalog");
    showFetchModals(offers.then(x => x.response));
    return (await offers).data;
}

export async function updateCatalog(changed: CatalogEntry[]): Promise<boolean> {
    let response = fetchPlain("/catalog", {
        method: "PATCH",
        body: JSON.stringify(changed),
        headers: {
            "Content-Type": "application/json"
        }
    });
    showFetchModals(response, "Сохранение...");
    return (await response).ok;
}
