import { PUBLIC_ALLOW_NON_HTTPS } from "$env/static/public";
import { BaseUrl, handleRequest } from "$lib";
import Cookies from "js-cookie";

export async function fetchAuthenticated(endpoint: string, init?: RequestInit): Promise<Response> {
    let token = Cookies.get("mpToken");

    if (!init) init = {};
    init.headers = new Headers(init.headers);
    init.headers.append("Authorization", "Bearer " + token);
    return fetch(BaseUrl + endpoint, init);
}

export async function login(name: string, password: string): Promise<boolean> {
    let credentials = { username: name, password };
    let promise = fetch(BaseUrl + "login", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: new URLSearchParams(credentials)
    });

    let ok = false;
    await handleRequest(promise, {
        errorHeader: "Не удалось войти в аккаунт",
        onSuccess: async response => {
            let body = await response.json();
            let token = body.access_token;
            Cookies.set("mpToken", token, {
                sameSite: "Lax",
                expires: 60 * 60 * 24 * 30,
                secure: !(PUBLIC_ALLOW_NON_HTTPS === "1")
            });
            ok = true;
        }
    });
    return ok;
}

export function logout() {
    Cookies.remove("mpToken");
}
