import { redirect, type Handle } from "@sveltejs/kit";

export const handle: Handle = async ({ event, resolve }) => {
    if (event.url.pathname === "/auth") {
        if (event.cookies.get("mpToken") !== undefined) {
            redirect(303, "/app");
        }
    } else if (event.url.pathname.startsWith("/app")) {
        if (event.cookies.get("mpToken") === undefined) {
            redirect(303, "/auth");
        }
    } else if (event.url.pathname === "/") {
        if (event.cookies.get("mpToken") === undefined) {
            redirect(303, "/auth");
        } else {
            redirect(303, "/app");
        }
    }
    const response = await resolve(event);
    return response;
};
