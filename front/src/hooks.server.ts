import type { Handle } from "@sveltejs/kit";

export const handle: Handle = async ({ event, resolve }) => {
    if (event.url.pathname.startsWith("/app"))
    {
        if (event.cookies.get("mpToken") === undefined)
        {
            return new Response('Redirect', {status: 302, headers: { Location: '/auth' }});
        }
    }
    const response = await resolve(event);
    return response;
};
