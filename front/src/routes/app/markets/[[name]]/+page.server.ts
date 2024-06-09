import { getStores, type Market } from "$lib/data/markets";
import { error } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ params, fetch }) => {
    let markets = await getStores({ fetch });
    markets.sort((a, b) => a.name.localeCompare(b.name));

    let market: Market | null;
    if (params.name === undefined) {
        market = null;
    } else {
        let found = markets.find(x => x.name === params.name);
        if (found === undefined) error(404, "Магазин не найден");
        market = found;
    }

    return {
        markets,
        market
    };
};
