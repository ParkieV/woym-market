import { fetchPlain } from "$lib/fetch";
import { showFetchModals } from "$lib/modal";
import { downloadFile } from "$lib/util";
import { get } from "svelte/store";
import { fboOffersSelection, fboStorageSelection } from "../../routes/app/(main)/state";

export abstract class Export {
    public async export(): Promise<{ ok: boolean }> {
        try {
            let promise = fetchPlain(this.url, {
                method: "POST",
                body: this.body,
                headers: { "Content-Type": "application/json" }
            });
            showFetchModals(promise, "Скачивание файла...", "Ошибка экспорта");
            let response = await promise;

            let blob = await response.blob();
            downloadFile(blob, this.defaultFileName);

            return { ok: true };
        } catch {
            return { ok: false };
        }
    }

    protected abstract get url(): string;
    protected abstract get body(): string;
    protected abstract get defaultFileName(): string;

    public abstract get valid(): boolean;
}

export class SimpleExport extends Export {
    public name_of_shop: string | null = null;
    public market: string | null = null;

    constructor(private url_: string) {
        super();
    }

    protected get url(): string {
        return this.url_;
    }

    protected get body(): string {
        let data: Record<string, string> = {};
        if (this.market) data.market = this.market;
        if (this.name_of_shop) data.name_of_shop = this.name_of_shop;
        return JSON.stringify(data);
    }

    protected get defaultFileName(): string {
        return "report.xlsx";
    }

    public get valid(): boolean {
        return true;
    }
}

export class OwnStorageExport extends Export {
    public place_id: number | null = null;
    public name_of_shop: string | null = null;
    public market: string | null = null;

    constructor() {
        super();
    }

    protected get url(): string {
        return `stocks/own-storage/export`;
    }

    protected get body(): string {
        let data: Record<string, string | number | number[] | null> = {
            place_id: this.place_id
        };
        if (this.name_of_shop) data.name_of_shop = this.name_of_shop;
        if (this.market) data.market = this.market;
        return JSON.stringify(data);
    }

    protected get defaultFileName() {
        return "report.xlsx";
    }

    public get valid(): boolean {
        return this.place_id !== null;
    }
}

export class SupplyExport extends Export {
    public type: "only-own-storage" | "only-stocks" | "with-own-storage" | null = null;
    public place_id: number | null = null;
    public name_of_shop: string | null = null;
    public market: string | null = null;

    constructor() {
        super();
    }

    protected get url(): string {
        return `stocks/supply/${this.type}/export`;
    }

    protected get body(): string {
        let data: Record<string, string | number | number[] | null> = {
            place_id: this.place_id,
            offers_id: Array.from(get(fboOffersSelection.filtered)).map(x => x[1].id),
            warehouses_id: Array.from(get(fboStorageSelection.filtered)).map(x => x[1].warehouse.id)
        };
        if (this.name_of_shop) data.name_of_shop = this.name_of_shop;
        if (this.market) data.market = this.market;
        return JSON.stringify(data);
    }

    protected get defaultFileName() {
        return "Поставка.zip";
    }

    public get valid(): boolean {
        return this.type !== null && (this.place_id !== null || !this.isPlaceNeeded);
    }

    public get isPlaceNeeded() {
        return this.type !== "only-stocks";
    }
}

export class ViolatorsExport extends Export {
    public market: string | null = null;
    public name_of_shop: string | null = null;

    protected get url(): string {
        return "data/violators/export";
    }

    protected get body(): string {
        let data: Record<string, string> = {};
        if (this.name_of_shop) data.name_of_shop = this.name_of_shop;
        if (this.market) data.market = this.market;
        return JSON.stringify(data);
    }

    protected get defaultFileName() {
        return "Нарушители.pdf";
    }

    public get valid(): boolean {
        return true;
    }
}
