import type { MyGridOptions } from "..";

/** Plugin for the grid. */
export interface GridPlugin<T> {
    /** Modifies `GridOptions`. */
    init?(opts: MyGridOptions<T>): Promise<void> | void;
}
