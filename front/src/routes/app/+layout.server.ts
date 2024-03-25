import { fetchUser } from "$lib/data/user";
import type { LayoutServerLoad } from "./$types";

export const load: LayoutServerLoad = async ({ fetch }) => {
    return {
        user: await fetchUser({ fetch })
    };
};
