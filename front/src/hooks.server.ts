import { token, tokenCookieName } from "$lib/user";
import { redirect, type Handle } from "@sveltejs/kit";
import { get } from "svelte/store";

export const handle: Handle = async ({ event, resolve }) => {
    token.set(event.cookies.get(tokenCookieName));

    if (event.url.pathname === "/auth") {
        if (get(token) !== undefined) {
            redirect(303, "/app");
        }
    } else if (event.url.pathname.startsWith("/app")) {
        if (get(token) === undefined) {
            redirect(303, "/auth");
        }
    } else if (event.url.pathname === "/") {
        if (get(token) === undefined) {
            redirect(303, "/auth");
        } else {
            redirect(303, "/app");
        }
    }
    const response = await resolve(event);
    return response;
};
