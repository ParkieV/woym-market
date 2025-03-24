import { fetchPlain } from "$lib/fetch";
import { showFetchModals } from "$lib/modal";
import { downloadFile } from "$lib/util";
import { get } from "svelte/store";
import { fboStorageSelection, fboStocksSelection } from "../../routes/app/(main)/selection";
import { getSelectedOrders } from "../../routes/app/(main)/fbo_storage/fbo-offer";
import { v4 } from "uuid";

export abstract class Export {
    public async export(): Promise<{ ok: boolean }> {
        try {
            const body = this.body;
            const headers: HeadersInit = body === null ? [] : [["Content-Type", "application/json"]];
            const promise = fetchPlain(this.url, { method: "POST", body, headers });
            showFetchModals(promise, "Скачивание файла...", "Ошибка экспорта");
            const response = await promise;

            const blob = await response.blob();
            downloadFile(blob, this.defaultFileName);

            return { ok: true };
        } catch {
            return { ok: false };
        }
    }

    protected abstract get url(): string;
    protected abstract get body(): string | null;
    protected abstract get defaultFileName(): string;

    public get valid(): boolean {
        return true;
    }
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
        const data: Record<string, string> = {};
        if (this.market) data.market = this.market;
        if (this.name_of_shop) data.name_of_shop = this.name_of_shop;
        return JSON.stringify(data);
    }

    protected get defaultFileName(): string {
        return "report.xlsx";
    }
}

export class CatalogExport extends Export {
    protected get url(): string {
        return `/catalog/export`;
    }

    protected get body(): string | null {
        return null;
    }

    protected get defaultFileName() {
        return "report.xlsx";
    }
}

export class OwnStorageExport extends Export {
    public place_id: number | null = null;

    constructor() {
        super();
    }

    protected get url(): string {
        return `/stocks/own-storage/export`;
    }

    protected get body(): string {
        const data: Record<string, string | number | number[] | null> = {
            place_id: this.place_id
        };
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

    protected get url(): string {
        return `/stocks/supply/${this.type}/export`;
    }

    protected get body(): string {
        const data: Record<string, string | number | number[] | null> = {
            place_id: this.place_id,
            offers_id: Array.from(get(fboStorageSelection.filtered)).map(x => x[1].id),
            warehouses_id: Array.from(get(fboStocksSelection.filtered)).map(x => x[1].warehouse.id)
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
        return "/offers/violators/export";
    }

    protected get body(): string {
        const data: Record<string, string> = {};
        if (this.name_of_shop) data.name_of_shop = this.name_of_shop;
        if (this.market) data.market = this.market;
        return JSON.stringify(data);
    }

    protected get defaultFileName() {
        return "Нарушители.pdf";
    }
}

export class DeliversExport extends Export {
    // При необходимости можно добавить дополнительные параметры для фильтрации:
    // public deliveryDate: string | null = null;
    // public courier: string | null = null;

    protected get url(): string {
        return `/v2/export/deliver`;
    }

    protected get body(): string | null {
        // Если нет необходимости передавать параметры, возвращаем null.
        // Если же нужны дополнительные данные, можно создать объект, например:
        /*
        const data: Record<string, string | null> = {};
        if (this.deliveryDate) data.deliveryDate = this.deliveryDate;
        if (this.courier) data.courier = this.courier;
        return JSON.stringify(data);
        */
        const data: Record<string, any> = {}
        data.orders = getSelectedOrders()
        data.session_id = v4()
        return JSON.stringify(data);
    }

    protected get defaultFileName(): string {
        return "Поставка.zip";
    }
}