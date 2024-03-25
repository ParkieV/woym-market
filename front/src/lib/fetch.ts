import { browser } from "$app/environment";
import Cookies from "js-cookie";
import { logout, tokenCookieName } from "./auth";
import { BaseUrl } from "$lib";
import { goto } from "$app/navigation";

export async function fetchPlain(endpoint: string, init?: FetchInit): Promise<Response> {
    if (!init) init = {};
    init.headers = new Headers(init.headers);

    addAuthorizationHeader(init.headers);

    const fetchFunc = init.fetch ?? fetch;

    return fetchFunc(BaseUrl + endpoint, init).then(redirectUnauthenticated);
}

export async function fetchJSON<T>(
    endpoint: string,
    init?: FetchInit
): Promise<{ data: T; response: Response }> {
    let promise = fetchPlain(endpoint, init);
    return promise.then(async r => ({
        data: await extractJSON<T>(r),
        response: r
    }));
}

function addAuthorizationHeader(headers: Headers) {
    if (browser) {
        const token = Cookies.get(tokenCookieName);
        headers.append("Authorization", "Bearer " + token);
    } else {
        // SvelteKit will handle server-side auth via handleFetch hook
    }
}

function redirectUnauthenticated(r: Response) {
    if (r.status === 401) {
        if (browser) {
            logout();
            goto("/auth");
        } else {
            // SvelteKit will handle server-side redirect via handleFetch hook
        }
    }
    return r;
}

function extractJSON<T>(r: Response): PromiseLike<T> {
    return r.json();
}

export type FetchInit = RequestInit & {
    fetch?: typeof fetch;
};
