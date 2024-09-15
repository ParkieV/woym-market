import { fetchPlain } from "$lib/fetch";
import { showFetchModals } from "$lib/modal";
import { uploadFile } from "$lib/util";

export abstract class Import {
    public async import(): Promise<{ ok: boolean }> {
        try {
            let url = this.url;

            let blob = await uploadFile();
            let body = this.body(blob);

            let promise = fetchPlain(url, { method: "POST", body });
            showFetchModals(promise, "Отправка файла...", "Ошибка импорта");
            await promise;
            return { ok: true };
        } catch {
            return { ok: false };
        }
    }

    protected abstract get url(): string;
    protected abstract body(file: Blob): FormData;

    public abstract get valid(): boolean;
}

export class OffersImport extends Import {
    constructor(public import_type: "table" | "prices" | "sizes") {
        super();
    }

    public market: string | null = null;
    public name_of_shop: string | null = null;

    protected get url(): string {
        return "offers/import";
    }

    protected body(file: Blob): FormData {
        let formData = new FormData();
        if (this.market) formData.append("market", this.market);
        if (this.name_of_shop) formData.append("name_of_shop", this.name_of_shop);
        if (this.import_type) formData.append("import_type", this.import_type);
        formData.append("data", file);
        return formData;
    }

    public get valid(): boolean {
        return true;
    }
}

export class CatalogImport extends Import {
    constructor(public kind: "table" | "prices" | "sizes") {
        super();
    }

    protected get url(): string {
        if (this.kind === "table") return "catalog/import";
        if (this.kind === "prices") return "catalog/import/prices";
        if (this.kind === "sizes") return "catalog/import/sizes";
        throw new Error("Неподдерживаемый вид импорта");
    }

    protected body(file: Blob): FormData {
        let formData = new FormData();
        formData.append("data", file);
        return formData;
    }

    public get valid(): boolean {
        return true;
    }
}

export class FboAdditionsImport extends Import {
    public props: FboAdditionsImportProps;

    constructor() {
        super();
        this.props = {
            name_of_shop: null,
            warehouse_id: null
        };
    }

    protected get url(): string {
        return "stocks/fbo/additions/import";
    }

    protected body(file: Blob): FormData {
        let formData = new FormData();
        formData.append("name_of_shop", this.props.name_of_shop ?? "");
        formData.append("warehouse_id", this.props.warehouse_id?.toFixed(0) ?? "");
        formData.append("data", file);
        return formData;
    }

    get valid(): boolean {
        return this.props.name_of_shop !== null && this.props.warehouse_id !== null;
    }
}

export type FboAdditionsImportProps = {
    name_of_shop: string | null;
    warehouse_id: number | null;
};

export class OwnStorageImport extends Import {
    public place_id: number | null = null;

    constructor(private subtype: "consumption" | "coming" | null) {
        super();
    }

    protected get url(): string {
        if (this.subtype === "coming") {
            return "stocks/own-storage/coming/import";
        } else if (this.subtype === "consumption") {
            return "stocks/own-storage/consumption/import";
        } else if (this.subtype === null) {
            return "stocks/own-storage/import";
        } else {
            throw new Error("Unexpected url type");
        }
    }

    protected body(file: Blob): FormData {
        let formData = new FormData();
        if (this.place_id) formData.append("place_id", this.place_id.toFixed(0));
        formData.append("data", file);
        return formData;
    }

    public get valid(): boolean {
        return this.place_id !== null;
    }
}
