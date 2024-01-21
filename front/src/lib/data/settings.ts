import { fetchAuthenticated } from "$lib/auth";

export type Settings = {
    /** Exchange rate (rubles per dollar). */
    rate: number;
};

export async function patchUserInfo(val: Settings): Promise<void> {
    let init: RequestInit = {
        method: "PATCH",
        body: JSON.stringify(val),
        headers: {
            "Content-Type": "application/json"
        }
    };
    await fetchAuthenticated("users/settings", init);
}

export async function fetchUserInfo(): Promise<Settings> {
    let info = await (await fetchAuthenticated("users/settings")).json();
    return info;
}
