import { handleRequest } from "$lib";
import { fetchAuthenticated } from "$lib/auth";

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

export async function patchUserInfo(val: Settings): Promise<boolean> {
    let init: RequestInit = {
        method: "PATCH",
        body: JSON.stringify(val),
        headers: {
            "Content-Type": "application/json"
        }
    };
    let promise = fetchAuthenticated("settings", init);
    let ok = false;
    handleRequest(promise, { header: "Сохранение...", onSuccess: () => (ok = true) });
    return ok;
}

export async function fetchUserInfo(): Promise<Settings> {
    let promise = fetchAuthenticated("settings");
    await handleRequest(promise);
    let info = await (await promise).json();
    return info;
}

export async function fetchLogs(): Promise<Logs> {
    return await (await fetchAuthenticated("settings/logs")).json();
}
