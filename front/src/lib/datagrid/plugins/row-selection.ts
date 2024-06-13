import { get, type Writable } from "svelte/store";
import type { GridPlugin } from ".";
import type { MyGridOptions } from "..";
import type { MyColDef, MyColGroupDef } from "../columns";

/**
 * Plugin to enable and manage row selection via checkbox.
 * */
export default class RowSelectionPlugin<T, K = T> implements GridPlugin<T> {
    constructor(
        private selected: Writable<Map<K, T>>,
        private options?: {
            key?: (val: T) => K;
            checkbox?: boolean;
            sync?: boolean;
        }
    ) {}

    init(opts: MyGridOptions<T>): void | Promise<void> {
        let {
            checkbox = true,
            key = (v: T) => v as unknown as K,
            sync = false
        } = this.options ?? {};

        opts.rowSelection = "multiple";

        let func = opts.onRowSelected;
        opts.onRowSelected = e => {
            let selected = get(this.selected);
            e.api.forEachNode(node => {
                if (node.data === undefined) return;
                if (!!node.isSelected()) {
                    selected.set(key(node.data), node.data);
                } else {
                    selected.delete(key(node.data));
                }
            });
            this.selected.set(selected);
            func?.(e);
        };

        let func2 = opts.onGridReady;
        opts.onGridReady = e => {
            const callback = (selected: Map<K, T>) => {
                e.api.forEachNode(node => {
                    if (node.data === undefined) return;
                    let isSelected = selected.has(key(node.data));
                    node.setSelected(isSelected);
                });
            };
            if (sync) {
                const unsubscribe = this.selected.subscribe(callback);
                e.api.addEventListener("gridPreDestroyed", () => unsubscribe());
            } else {
                callback(get(this.selected));
            }

            func2?.(e);
        };

        apply(opts.columnDefs);
        function apply(cols: (MyColDef | MyColGroupDef)[]) {
            for (const col of cols) {
                if ("children" in col) {
                    apply(col.children);
                } else {
                    if (col.source.pinned) {
                        col.checkboxSelection = checkbox;
                        col.headerCheckboxSelection = checkbox;
                        col.headerCheckboxSelectionFilteredOnly = checkbox;
                    }
                }
            }
        }
    }
}
