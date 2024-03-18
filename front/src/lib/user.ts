import { type Writable, writable, type Readable, derived, get } from "svelte/store";
import { fetchAuthenticated } from "./auth";
import { browser } from "$app/environment";
import Cookies from "js-cookie";
import { PUBLIC_ALLOW_NON_HTTPS } from "$env/static/public";

export const user: Writable<User | undefined> = writable();
export const userCanModify: Readable<boolean> = derived(user, x => x?.is_staff ?? false);

export const tokenCookieName = "mpToken";

const _token: Writable<string | undefined> = writable(undefined);
export const token: Writable<string | undefined> = {
    set: val => {
        if (browser) {
            if (val === undefined) {
                Cookies.remove(tokenCookieName);
            } else {
                Cookies.set(tokenCookieName, val, {
                    sameSite: "Lax",
                    expires: 60 * 60 * 24 * 30,
                    secure: !(PUBLIC_ALLOW_NON_HTTPS === "1")
                });
            }
        }
        _token.set(val);
    },
    subscribe: _token.subscribe,
    update: updater => {
        let val = updater(get(token));
        token.set(val);
    }
};
if (browser && get(token) === undefined) token.set(Cookies.get(tokenCookieName));

export async function fetchUser() {
    try {
        let response = await fetchAuthenticated("users/me");
        let data: User = await response.json();
        user.set(data);
    } catch {}
}

export type User = {
    id: number;
    login: string;
    is_staff: boolean;
};
