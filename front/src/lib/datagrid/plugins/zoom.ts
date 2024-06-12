import type { GridPlugin } from ".";
import type { MyGridOptions } from "..";
import type { MyColDef, MyColGroupDef } from "../columns";
import { ImageColumn } from "../columns/types";

/**
 * Plugin to zoom images on click.
 *
 * Checks whether clicked column is an instance of {@link ImageColumn}.
 *
 * @param onClick Callback to call on click.
 * */
export default class ZoomPlugin<T> implements GridPlugin<T> {
    constructor(private onClick: OnClickCallback) {}

    init(opts: MyGridOptions<T>): void | Promise<void> {
        let onClick = this.onClick;
        apply(opts.columnDefs);

        function apply(cols: (MyColDef | MyColGroupDef)[]) {
            for (const col of cols) {
                if ("children" in col) {
                    apply(col.children);
                } else {
                    if (col.source.base instanceof ImageColumn) {
                        let func = col.onCellClicked;
                        col.onCellClicked = args => {
                            onClick(args.value);
                            func?.(args);
                        };
                    }
                }
            }
        }
    }
}

type OnClickCallback = (href: string) => any | Promise<any>;
