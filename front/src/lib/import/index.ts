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

export class SimpleImport extends Import {
    public props: SimpleImportProps;

    constructor(url: string, type?: string) {
        super();
        this.props = {
            url,
            import_type: type,
            market: null,
            name_of_shop: null
        };
    }

    protected get url(): string {
        return this.props.url;
    }

    protected body(file: Blob): FormData {
        let formData = new FormData();
        if (this.props.market) formData.append("market", this.props.market);
        if (this.props.name_of_shop) formData.append("name_of_shop", this.props.name_of_shop);
        if (this.props.import_type) formData.append("import_type", this.props.import_type);
        formData.append("data", file);
        return formData;
    }

    public get valid(): boolean {
        return true;
    }
}

export type SimpleImportProps = {
    import_type?: string;
    url: string;
    market: string | null;
    name_of_shop: string | null;
};

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
