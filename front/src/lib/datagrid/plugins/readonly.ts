import type { GridPlugin } from ".";
import type { MyGridOptions } from "..";
import type { MyColDef, MyColGroupDef } from "../columns";

/** Applies class rules to grid. */
export default class ReadonlyPlugin<T> implements GridPlugin<T> {
    constructor(private enable: boolean) {}

    init(opts: MyGridOptions<T>): void | Promise<void> {
        if (!this.enable) return;

        apply(opts.columnDefs);

        function apply(cols: (MyColDef<T> | MyColGroupDef<T>)[]) {
            for (const col of cols) {
                if ("children" in col) {
                    apply(col.children);
                } else {
                    col.editable = false;
                }
            }
        }
    }
}
