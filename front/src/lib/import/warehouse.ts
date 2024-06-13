import Import from ".";

export default class WarehouseImport extends Import {
    public kind: WarehouseImportKind = "fbo-yandex";
    public name_of_shop: string | null = null;
    public warehouse_id: number | null = null;

    get url(): string {
        if (this.name_of_shop === null || this.warehouse_id === null) throw new Error();

        let params: Record<string, string> = {};
        params["warehouse_id"] = this.warehouse_id.toFixed(0);
        params["name_of_shop"] = this.name_of_shop;

        let url = "stocks/fbo/import?" + new URLSearchParams(params);
        return url;
    }

    get valid(): boolean {
        return this.name_of_shop !== null && this.warehouse_id !== null;
    }

    public static matchKind(kind: string): boolean {
        return warehoureImportKinds.includes(kind as WarehouseImportKind);
    }
}

export type WarehouseImportKind = (typeof warehoureImportKinds)[number];
export const warehoureImportKinds = ["fbo-yandex"] as const;
