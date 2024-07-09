import { getStores } from "$lib/data/markets";
import { writable } from "svelte/store";
import type { LayoutLoad } from "./$types";

export const load: LayoutLoad = async ({ fetch }) => {
    return {
        markets: await getStores({ fetch }),
        search: writable("")
    };
};
