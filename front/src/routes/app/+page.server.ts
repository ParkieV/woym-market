import { fetchOfferList } from "$lib";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({}) => {
    return {
        offers: await fetchOfferList()
    };
};
