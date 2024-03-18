import { fetchSettings } from "$lib/data/settings";
import type { PageLoad } from "./$types";

export const load: PageLoad = async () => {
    return {
        settings: await fetchSettings()
    };
};
