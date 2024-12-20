import { getStores } from "$lib/data/markets";
import { error } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ params, fetch }) => {
    const markets = await getStores({ fetch });
    markets.sort((a, b) => a.name.localeCompare(b.name));

    const { market, shop } = params;

    if (market === undefined || shop === undefined) {
        return {
            markets,
            market: null
        };
    }

    const found = markets.find(x => x.type === market && x.name === shop);
    if (found === undefined) error(404, "Магазин не найден");

    return {
        markets,
        market: found
    };
};
