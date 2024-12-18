import { fetchTemplates } from "$lib/data/templates";
import type { PageLoad } from "./$types";

export const load: PageLoad = async () => {
    return {
        templates: await fetchTemplates()
    };
};
