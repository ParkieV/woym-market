import Cookies from "js-cookie";
import { fetchPlain } from "./fetch";
import { showFetchModals } from "./modal";

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
        Cookies.set(tokenCookieName, body.access_token);
        return true;
    } else {
        return false;
    }
}

export function logout() {
    Cookies.remove(tokenCookieName);
}
