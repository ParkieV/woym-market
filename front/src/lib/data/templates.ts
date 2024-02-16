import { handleRequest } from "$lib";
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
    let promise = fetchAuthenticated("data/pricing-schemes");
    await handleRequest(promise);
    let templates: Template[] = await (await promise).json();
    templates.sort((a, b) => a.id - b.id);
    return templates;
}

export async function patchTemplates(templates: Template[]): Promise<boolean> {
    let promises = templates.map(template => {
        return fetchAuthenticated("data/pricing-schemes", {
            method: "PATCH",
            body: JSON.stringify(template),
            headers: {
                "Content-Type": "application/json"
            }
        });
    });

    let ok = false;
    await handleRequest(Promise.all(promises), {
        header: "Сохранение...",
        onSuccess: () => (ok = true)
    });
    return ok;
}
