import Cookies from "js-cookie";
import { fetchPlain } from "./fetch";
import { showFetchModals } from "./modal";
import { PUBLIC_ALLOW_NON_HTTPS } from "$env/static/public";

export const tokenCookieName = "mpToken";

export async function login(name: string, password: string): Promise<boolean> {
    let credentials = { username: name, password };
    let promise = fetchPlain("login", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: new URLSearchParams(credentials)
    });

    showFetchModals(promise, undefined, "Не удалось войти в аккаунт");

    let response = await promise;
    if (response.ok) {
        let body = await response.json();
        Cookies.set(tokenCookieName, body.access_token, {
            sameSite: "Lax",
            expires: 60 * 60 * 24 * 30,
            secure: !(PUBLIC_ALLOW_NON_HTTPS === "1"),
            path: "/"
        });
        return true;
    } else {
        return false;
    }
}

export function logout() {
    Cookies.remove(tokenCookieName);
}
