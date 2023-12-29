import { BaseUrl } from '$lib';
import { persisted } from 'svelte-persisted-store'
import { get, type Readable, type Writable } from 'svelte/store';

const _Token: Writable<string | null> = persisted('token', null);
export const Token: Readable<string | null> = _Token;

export async function Login(name: string, password: string): Promise<boolean>
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
    document.cookie = `mpToken=${token}; max-age=3600; secure`;

    return true;
}

export function Logout()
{
    _Token.set(null);
    document.cookie = `mpToken=; max-age=0;`;
}
