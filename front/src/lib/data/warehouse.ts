import { fetchJSON, type FetchInit } from "$lib/fetch";
import { showFetchModals } from "$lib/modal";

export type Warehouse = {
    id: number;
    name: string;
    warehouse_type: WarehouseType;
    market: string;
    from_file_updated_at: string | null;
};

export type WarehouseType = "warehouse" | "cluster";

export async function getWarehouses(init?: FetchInit): Promise<Warehouse[]> {
    let promise = fetchJSON<Warehouse[]>("stocks/warehouses", init);
    showFetchModals(
        promise.then(x => x.response),
        undefined,
        "Не удалось получить список складов"
    );
    return (await promise).data;
}
