import type { CellClassRules } from "ag-grid-enterprise";
import type { GridPlugin } from ".";
import type { MyGridOptions } from "..";
import type { MyColDef, MyColGroupDef } from "../columns";

/** Applies class rules to grid. */
export default class ClassesPlugin<T> implements GridPlugin<T> {
    constructor(private rules?: CellClassRules) {}

    init(opts: MyGridOptions<T>): void | Promise<void> {
        let rules = this.rules;

        apply(opts.columnDefs);

        function apply(cols: (MyColDef<T> | MyColGroupDef<T>)[]) {
            for (const col of cols) {
                if ("children" in col) {
                    apply(col.children);
                } else {
                    col.cellClassRules = {
                        ...col.cellClassRules,
                        editable: ({ colDef: { editable } }) => editable === true,
                        ...rules
                    };
                }
            }
        }
    }
}
