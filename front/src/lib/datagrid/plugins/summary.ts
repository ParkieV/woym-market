import type { GridApi } from "ag-grid-enterprise";
import type { GridPlugin } from ".";
import type { MyGridOptions } from "..";
import type { MyColDef, MyColGroupDef } from "../columns";

export class SummaryPlugin<T> implements GridPlugin<T> {
    constructor(private getters: Partial<Record<keyof T, Getter<T>>>) {}
    init(opts: MyGridOptions<T>): void | Promise<void> {
        this.apply(opts.columnDefs);

        let ready = opts.onGridReady;
        opts.onGridReady = e => {
            e.api.addEventListener("refreshSummary", () => {
                this.setData(e.api);
            });
            ready?.(e);
        };

        let onRowData = opts.onRowDataUpdated;
        opts.onRowDataUpdated = e => {
            setTimeout(() => this.setData(e.api), 0);
            onRowData?.(e);
        };

        let onChanged = opts.onCellValueChanged;
        opts.onCellValueChanged = e => {
            this.setData(e.api);
            onChanged?.(e);
        };

        let onSelection = opts.onSelectionChanged;
        opts.onSelectionChanged = e => {
            this.setData(e.api);
            onSelection?.(e);
        };
    }

    private apply(cols: (MyColDef<T> | MyColGroupDef<T>)[]) {
        for (const col of cols) {
            if ("children" in col) {
                this.apply(col.children);
            } else {
                if (typeof col.valueGetter === "function") {
                    let getter = col.valueGetter;
                    col.valueGetter = e => {
                        if (e.node && e.node.isRowPinned()) {
                            if (col.field === undefined) return null;
                            return e.data?.[col.field as any as keyof T];
                        } else {
                            return getter(e);
                        }
                    };
                }

                if (typeof col.valueFormatter !== "string") {
                    let formatter = col.valueFormatter;
                    col.valueFormatter = e => {
                        if (e.node && e.node.isRowPinned()) {
                            if (e.value === null || e.value === undefined) return "";
                            else return formatter?.(e) ?? e.value.toString();
                        }
                        return formatter?.(e) ?? e.value.toString();
                    };
                }

                let selector = col.cellRendererSelector;
                col.cellRendererSelector = e => {
                    if (e.node.isRowPinned()) {
                        return {};
                    } else {
                        return selector?.(e);
                    }
                };

                if (col.cellClassRules) {
                    let editable = col.cellClassRules.editable;
                    col.cellClassRules.editable = e => {
                        if (e.node.isRowPinned()) {
                            return false;
                        } else {
                            if (typeof editable === "string") {
                                throw new Error("string cellClassRule is not supported");
                            } else {
                                return editable(e);
                            }
                        }
                    };
                }
            }
        }
    }

    private setData(api: GridApi<T>) {
        let rows = api.getSelectedRows();
        if (rows.length === 0) rows = api.getGridOption("rowData") ?? [];

        let data: Record<string, any> = {};
        for (const key in this.getters) {
            data[key] = this.getters[key]?.({ api, rows });
        }
        api.setGridOption("pinnedBottomRowData", [data]);
    }
}

export type Getter<T> = (event: GetterParams<T>) => void;

export type GetterParams<T> = { api: GridApi<T>; rows: T[] };
