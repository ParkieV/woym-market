import { fetchJSON, fetchPlain } from "$lib/fetch";
import { showFetchModals } from "$lib/modal";

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
    let r = fetchJSON<Template[]>("offers/pricing-schemes");
    showFetchModals(r.then(x => x.response));
    let templates: Template[] = (await r).data;
    templates.sort((a, b) => (a.name > b.name ? 1 : b.name > a.name ? -1 : 0));
    return templates;
}

export async function patchTemplates(templates: Template[]): Promise<boolean> {
    let promise = Promise.all(templates.map(patchTemplate));
    showFetchModals(promise, "Сохранение...");
    return (await promise).every(r => r.ok);
}

async function patchTemplate(template: Template): Promise<Response> {
    return fetchPlain("offers/pricing-schemes", {
        method: "PATCH",
        body: JSON.stringify(template),
        headers: {
            "Content-Type": "application/json"
        }
    });
}
