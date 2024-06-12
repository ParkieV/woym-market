import type { GridOptions } from "ag-grid-enterprise";

/** Grid options used in all grids. */
export const BASE_GRID_OPTIONS: GridOptions = {
    suppressDragLeaveHidesColumns: true,
    rowHeight: 75,
    tooltipShowDelay: 500,
    enableRangeSelection: true,
    enableRangeHandle: true,
    suppressRowClickSelection: true,

    getContextMenuItems: () => ["cut", "copy", "paste"],
    localeText: {
        cut: "Вырезать",
        copy: "Копировать",
        paste: "Вставить"
    }
};
