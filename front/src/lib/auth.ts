import { BaseUrl } from "$lib";
import Cookies from "js-cookie";

export async function fetchAuthenticated(endpoint: string, init?: RequestInit): Promise<Response> {
    let token = Cookies.get("mpToken");
    if (!token) throw new Error("403");

    if (!init) init = {};
    init.headers = new Headers(init.headers);
    init.headers.append("Authorization", "Bearer " + token);
    return fetch(BaseUrl + endpoint, init);
}

export async function login(name: string, password: string): Promise<boolean> {
    let credentials = { username: name, password };
    let response = await fetch(BaseUrl + "login", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: new URLSearchParams(credentials)
    });
    if (response.status != 200) return false;

    let body = await response.json();
    let token = body.access_token;

    Cookies.set("mpToken", token, {
        sameSite: "Lax",
        expires: 60 * 60 * 24 * 30,
        secure: true
    });

    return true;
}

export function logout() {
    Cookies.remove("mpToken");
}
