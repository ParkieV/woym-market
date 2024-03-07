import { handleRequest } from "$lib";
import { fetchAuthenticated } from "$lib/auth";
import type { Market } from "./markets";

export type Settings = {
    /** Exchange rate (rubles per dollar). */
    rate: number;
    /** Discount for common items in percent. */
    discount_purchase: number;
    /** Fee for sale through FBY in percent. */
    fby_sales_commission: number;
};

export type Logs = {
    updated_at: string | null;
};

export async function fetchSettings(): Promise<Settings & { markets: Market[] }> {
    let main_promise = fetchAuthenticated("settings");
    let markets_promise = fetchAuthenticated("settings/markets");

    let settings = await handleRequest(Promise.all([main_promise, markets_promise]), {
        onSuccess: async ([main_response, markets_response]) => {
            let [main_settings, markets] = await Promise.all([
                main_response.json() as Promise<Settings>,
                markets_response.json() as Promise<Market[]>
            ]);
            return {
                ...main_settings,
                markets
            };
        }
    });
    return settings!;
}

export async function patchSettings(settings: Settings & { markets: Market[] }) {
    let settings_promise = fetchAuthenticated("settings", {
        method: "PATCH",
        body: JSON.stringify({
            discount_purchase: settings.discount_purchase,
            fby_sales_commission: settings.fby_sales_commission,
            rate: settings.rate
        } satisfies Settings),
        headers: {
            "Content-Type": "application/json"
        }
    });
    let market_promises = settings.markets.map(x => {
        return fetchAuthenticated(`settings/markets/${x.id}`, {
            method: "PATCH",
            body: JSON.stringify({ tax: x.tax }),
            headers: {
                "Content-Type": "application/json"
            }
        });
    });
    let promise = Promise.all([settings_promise, ...market_promises]);
    await handleRequest(promise, { header: "Сохранение..." });
}

export async function fetchLogs(): Promise<Logs> {
    return await (await fetchAuthenticated("settings/logs")).json();
}
