import { env } from "$env/dynamic/public";
import { tokenCookieName } from "$lib/auth";
import { redirect, type Handle, type HandleFetch } from "@sveltejs/kit";

export const handle: Handle = async ({ event, resolve }) => {
    event.locals.token = event.cookies.get(tokenCookieName);

    if (event.url.pathname === "/auth") {
        if (event.locals.token !== undefined) {
            redirect(303, "/backend");
        }
    } else if (event.url.pathname.startsWith("/backend")) {
        if (event.locals.token === undefined) {
            redirect(303, "/auth");
        }
    } else if (event.url.pathname === "/") {
        if (event.locals.token === undefined) {
            redirect(303, "/auth");
        } else {
            redirect(303, "/backend");
        }
    }
    const response = await resolve(event);
    return response;
};

export const handleFetch: HandleFetch = async ({ event: { cookies }, request, fetch }) => {
    let token = cookies.get(tokenCookieName);
    if (token !== undefined &&
        (request.url.startsWith(env.PUBLIC_BASE_URL!) || request.url.startsWith(env.PUBLIC_LOCAL_BASE_URL!))) {
        token = `Bearer ${token}`;
        request.headers.set("Authorization", token);
    }
    return fetch(request).then(r => {
        if (r.status === 401) {
            cookies.delete(tokenCookieName, { path: "/" });
            redirect(303, "/auth");
        }
        return r;
    });
};
