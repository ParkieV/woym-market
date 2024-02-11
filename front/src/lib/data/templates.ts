import { fetchAuthenticated } from "$lib/auth";

export type Template = {
    id: number;
    name: string;

    use_total_price: boolean;
    use_attractive_price_threshold: boolean;
    use_moderately_attractive_price_threshold: boolean;
    use_your_price_for_buyers: boolean;
    use_min_price_in_market: boolean;
    use_min_price_without_market: boolean;
    use_min_general_markets_price: boolean;

    /** Number that the resulting price will be divided by. */
    n: number;
    /** Amount that will be added to the price (in percent). */
    m: number;
};

export async function fetchTemplates(): Promise<Template[]> {
    let templates: Template[] = await (await fetchAuthenticated("data/pricing-schemes")).json();
    templates.sort((a, b) => a.id - b.id);
    return templates;
}

export async function patchTemplate(template: Template) {
    fetchAuthenticated("data/pricing-schemes", {
        method: "PATCH",
        body: JSON.stringify(template),
        headers: {
            "Content-Type": "application/json"
        }
    });
}
