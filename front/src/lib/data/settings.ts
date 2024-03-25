import { fetchJSON, fetchPlain } from "$lib/fetch";
import { showFetchModals } from "$lib/modal";
import type { Market } from "./markets";

export type Settings = {
    /** Exchange rate (rubles per dollar). */
    rate: number;
    /** Discount for common items in percent. */
    discount_purchase: number;
    /** Fee for sale through FBY in percent. */
    fbo_sales_commission: number;
};

export type Logs = {
    updated_at: string | null;
};

export async function fetchSettings(): Promise<Settings & { markets: Market[] }> {
    let main_promise = fetchJSON<Settings>("settings");
    let markets_promise = fetchJSON<Market[]>("settings/markets");
    let promise = Promise.all([main_promise, markets_promise]);

    showFetchModals(promise.then(x => x.map(x => x.response)));

    let [main_settings, markets] = await promise;
    return {
        ...main_settings.data,
        markets: markets.data
    };
}

export async function patchSettings(settings: Settings & { markets: Market[] }) {
    let settings_promise = fetchPlain("settings", {
        method: "PATCH",
        body: JSON.stringify({
            discount_purchase: settings.discount_purchase,
            fbo_sales_commission: settings.fbo_sales_commission,
            rate: settings.rate
        } satisfies Settings),
        headers: {
            "Content-Type": "application/json"
        }
    });
    let market_promises = settings.markets.map(x => {
        return fetchPlain(`settings/markets/${x.id}`, {
            method: "PATCH",
            body: JSON.stringify({ tax: x.tax }),
            headers: {
                "Content-Type": "application/json"
            }
        });
    });
    let promise = Promise.all([settings_promise, ...market_promises]);
    showFetchModals(promise, "Сохранение...");
}

export async function fetchLogs(): Promise<Logs> {
    return fetchJSON<Logs>("settings/logs").then(x => x.data);
}
