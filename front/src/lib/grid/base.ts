import { userCanModify } from "$lib/data/user";
import type { GridOptions } from "ag-grid-enterprise";
import { get } from "svelte/store";

/** Grid options used in all grids. */
export const BASE_GRID_OPTIONS: GridOptions = {
    suppressDragLeaveHidesColumns: true,
    rowHeight: 75,
    tooltipShowDelay: 500,
    enableRangeSelection: true,
    enableRangeHandle: true,
    suppressRowClickSelection: true,

    getContextMenuItems: () => (get(userCanModify) ? ["cut", "copy", "paste"] : ["copy"]),
    localeText: {
        cut: "Вырезать",
        copy: "Копировать",
        paste: "Вставить"
    }
};
