import type { CellClassRules, ColDef, ColGroupDef } from "ag-grid-enterprise";
import type { GridDefinition, GridPlugin } from "..";

/** Applies class rules to grid. */
export default function ClassesPlugin<T>(rules?: CellClassRules): GridPlugin {
    return (grid: GridDefinition) => {
        if (grid.options.columnDefs) {
            apply(grid.options.columnDefs);
        }

        function apply(cols: (ColDef<T> | ColGroupDef<T>)[]) {
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
    };
}
