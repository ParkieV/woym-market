import Import from ".";

export default class SimpleImport extends Import {
    public kind: SimpleImportKind = "table";
    public market: string | null = null;
    public name_of_shop: string | null = null;

    get url(): string {
        let params: Record<string, string> = {};
        params["kind"] = this.kind;
        if (this.market !== null) params["market"] = this.market;
        if (this.name_of_shop !== null) params["name_of_shop"] = this.name_of_shop;

        let url = "data/import?" + new URLSearchParams(params);
        return url;
    }

    get valid(): boolean {
        return true;
    }

    public static matchKind(kind: string): boolean {
        return simpleImportKinds.includes(kind as SimpleImportKind);
    }
}

export type SimpleImportKind = (typeof simpleImportKinds)[number];
export const simpleImportKinds = [
    "table",
    "sizes",
    "prices",
    "matrix-fbo-stocks",
    "matrix-own-storage"
] as const;
