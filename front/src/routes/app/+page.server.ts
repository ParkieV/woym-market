import type { ColDef } from "ag-grid-community";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ fetch }) => {
    let offers = await ((await fetch("http://5.35.88.225:8000/offers/")).json())
    return {
        offers,
    };
};
