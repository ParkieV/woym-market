import { createGrid, type GridApi, type GridOptions } from "ag-grid-enterprise";
import {
    getColumns,
    type Column,
    type ColumnGroup,
    type MyColDef,
    type MyColGroupDef
} from "./columns";
import type { GridPlugin } from "./plugins";

/** Grid definition used to create Grid component. */
export class GridDefinition<T = any> {
    public options: MyGridOptions<T>;
    public plugins: GridPlugin<T>[] = [];

    constructor(options: GridOptions, columns: (Column | ColumnGroup)[]) {
        this.options = {
            ...options,
            columnDefs: getColumns<T>(columns)
        };
    }

    /** Register plugin. */
    public plugin(plugin: GridPlugin<T>): GridDefinition<T> {
        this.plugins.push(plugin);
        return this;
    }

    /** Applies all registered plugins and creates a grid instance. */
    public async build(element: HTMLElement): Promise<GridApi<T>> {
        for (const plugin of this.plugins) {
            await plugin.init?.(this.options);
        }
        return createGrid(element, this.options);
    }
}

/** {@link GridOptions} with preserved translation source. */
export type MyGridOptions<T> = GridOptions<T> & {
    columnDefs: (MyColDef<T> | MyColGroupDef<T>)[];
};
