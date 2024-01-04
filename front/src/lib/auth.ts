import { BaseUrl } from '$lib';
import { persisted } from 'svelte-persisted-store'
import { get, type Readable, type Writable } from 'svelte/store';

const _Token: Writable<string | null> = persisted('token', null);
export const Token: Readable<string | null> = _Token;

export async function fetchAuthenticated(endpoint: string, init?: RequestInit): Promise<Response> {
    let token = get(Token);
    if (!token) throw new Error("403");

    if (!init) init = {};
    init.headers = new Headers(init.headers);
    init.headers.append("Authorization", "Bearer " + token);
    return fetch(BaseUrl + endpoint, init);
}

export async function login(name: string, password: string): Promise<boolean>
{
    let credentials = { username: name, password };
    let response = await fetch(
        BaseUrl + "login",
        {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: new URLSearchParams(credentials)
        }
    );
    if (response.status != 200) return false;

    let body = await response.json();
    let token = body.access_token;

    _Token.set(token);
    // TODO: Add `secure; ` field if https is implemented.
    document.cookie = `mpToken=${token}; max-age=3600`;

    return true;
}

export function logout()
{
    _Token.set(null);
    document.cookie = `mpToken=; max-age=0;`;
}
