import { getStores } from "$lib/data/markets";
import type { LayoutLoad } from "./$types";

export const load: LayoutLoad = async () => {
    return {
        options: await getStores()
    };
};
