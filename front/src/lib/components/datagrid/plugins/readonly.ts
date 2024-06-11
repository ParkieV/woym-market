import type { ColDef, ColGroupDef } from "ag-grid-enterprise";
import type { GridDefinition, GridPlugin } from "..";

/** Makes the whole grid readonly. */
export default function ReadonlyPlugin(enable: boolean): GridPlugin {
    if (!enable) return () => {};
    return (grid: GridDefinition) => {
        if (grid.options.columnDefs) {
            apply(grid.options.columnDefs);
        }

        function apply(cols: (ColDef | ColGroupDef)[]) {
            for (const col of cols) {
                if ("children" in col) {
                    apply(col.children);
                } else {
                    col.editable = false;
                }
            }
        }
    };
}
