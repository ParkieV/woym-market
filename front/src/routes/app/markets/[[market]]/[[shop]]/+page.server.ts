import { getStores } from "$lib/data/markets";
import { error } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ params, fetch }) => {
    let markets = await getStores({ fetch });
    markets.sort((a, b) => a.name.localeCompare(b.name));

    let { market, shop } = params;

    if (market === undefined || shop === undefined) {
        return {
            markets,
            market: null
        };
    }

    let found = markets.find(x => x.type === market && x.name === shop);
    if (found === undefined) error(404, "Магазин не найден");

    return {
        markets,
        market: found
    };
};
