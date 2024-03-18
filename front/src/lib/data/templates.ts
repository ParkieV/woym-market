import { handleRequest } from "$lib";
import { fetchAuthenticated } from "$lib/auth";

export type Template = {
    name: string;
    market: string;
    /** Number that the resulting price will be divided by. */
    n: number;
    /** Amount that will be added to the price (in percent). */
    m: number;
    fields: [
        {
            id: number;
            key: string;
            name: string;
            value: boolean;
            pricing_scheme_name: string;
        }
    ];
};

export async function fetchTemplates(): Promise<Template[]> {
    let promise = fetchAuthenticated("data/pricing-schemes");
    await handleRequest(promise);
    let templates: Template[] = await (await promise).json();
    templates.sort((a, b) => (a.name > b.name ? 1 : b.name > a.name ? -1 : 0));
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
