import type { Readable } from "svelte/store";
import type { GridPlugin } from ".";
import type { MyGridOptions } from "..";

/** Applies filter to the grid. */
export default class FilterPlugin<T> implements GridPlugin<T> {
    constructor(private filter: Readable<Filter<T>>) {}

    init(opts: MyGridOptions<T>): void | Promise<void> {
        let func = opts.onGridReady;
        opts.onGridReady = e => {
            this.filter.subscribe(filter => {
                e.api.setGridOption(
                    "doesExternalFilterPass",
                    ({ data }) => data === undefined || filter(data)
                );
                e.api.setGridOption("isExternalFilterPresent", () => true);
                e.api.onFilterChanged();
            });
            func?.(e);
        };
    }
}

type Filter<T> = (data: T) => boolean;
