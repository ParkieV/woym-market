import type { GridOptions } from "ag-grid-enterprise";
import {
    getColumns,
    type Column,
    type ColumnGroup,
    type MyColDef,
    type MyColGroupDef
} from "./columns";

/** Grid definition used to create Grid component. */
export class GridDefinition<T = any> {
    public options: MyGridOptions<T>;
    private plugins: GridPlugin[] = [];

    constructor(options: GridOptions, columns: (Column | ColumnGroup)[]) {
        this.options = {
            ...options,
            columnDefs: getColumns<T>(columns)
        };
    }

    /** Register plugin. */
    public plugin(plugin: GridPlugin): GridDefinition {
        this.plugins.push(plugin);
        return this;
    }

    /** Applies all registered plugins */
    public async build(): Promise<GridOptions<T>> {
        for (const plugin of this.plugins) {
            await plugin(this);
        }
        return this.options;
    }
}

/**
 * Plugin for the grid.
 *
 * Basically a function that modifies {@link GridDefinition}.
 * */
export type GridPlugin = (def: GridDefinition) => Promise<void> | void;

/** {@link GridOptions} with preserved translation source. */
export type MyGridOptions<T> = GridOptions<T> & {
    columnDefs: (MyColDef<T> | MyColGroupDef<T>)[];
};
