import type { Writable } from "svelte/store";
import type { GridPlugin } from ".";
import type { MyGridOptions } from "..";
import type { MyColDef, MyColGroupDef } from "../columns";

/**
 * Plugin to enable and manage row selection via checkbox.
 * */
export default class RowSelectionPlugin<T> implements GridPlugin<T> {
    constructor(
        private selected: Writable<Set<T>>,
        private options?: {
            checkbox: boolean;
        }
    ) {}

    init(opts: MyGridOptions<T>): void | Promise<void> {
        let { checkbox = true } = this.options ?? {};

        opts.rowSelection = "multiple";

        let func = opts.onRowSelected;
        opts.onRowSelected = e => {
            let isSelected = !!e.node.isSelected();
            if (isSelected) {
                this.selected.update(data => {
                    if (e.node.data !== undefined) data.add(e.node.data);
                    return data;
                });
            } else {
                this.selected.update(data => {
                    if (e.node.data !== undefined) data.delete(e.node.data);
                    return data;
                });
            }
            const { rowPinned } = e;
            rowPinned;
            func?.(e);
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
