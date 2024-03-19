import { BaseUrl, handleRequest } from "$lib";
import { get } from "svelte/store";
import { token } from "./user";

export async function fetchAuthenticated(endpoint: string, init?: RequestInit): Promise<Response> {
    if (!init) init = {};
    init.headers = new Headers(init.headers);
    init.headers.append("Authorization", "Bearer " + get(token));
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
            token.set(body.access_token);
            ok = true;
        }
    });
    return ok;
}

export function logout() {
    token.set(undefined);
}
