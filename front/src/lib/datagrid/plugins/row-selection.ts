import { get, type Writable } from "svelte/store";
import type { GridPlugin } from ".";
import type { MyGridOptions } from "..";
import type { MyColDef, MyColGroupDef } from "../columns";
import type { Selection } from "$lib/selection";

/**
 * Plugin to enable and manage row selection via checkbox.
 * */
export default class RowSelectionPlugin<T, K> implements GridPlugin<T> {
    constructor(
        private selection: Selection<T, K>,
        private options: {
            key: (val: T) => K;
            checkbox?: boolean;
            sync?: boolean;
        }
    ) {}

    init(opts: MyGridOptions<T>): void | Promise<void> {
        let { checkbox = true, key, sync = false } = this.options ?? {};

        opts.rowSelection = "multiple";

        let func = opts.onRowSelected;
        opts.onRowSelected = e => {
            let selected = get(this.selection.selected);
            e.api.forEachNode(node => {
                if (node.data === undefined) return;
                if (!!node.isSelected()) {
                    selected.set(key(node.data), node.data);
                } else {
                    selected.delete(key(node.data));
                }
            });
            this.selection.selected.set(selected);
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
                const unsubscribe = this.selection.selected.subscribe(callback);
                e.api.addEventListener("gridPreDestroyed", () => unsubscribe());
            } else {
                callback(get(this.selection.selected));
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
