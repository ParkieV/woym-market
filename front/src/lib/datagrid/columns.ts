import { fetchAuthenticated } from "$lib/auth";
import type { ColDef, GridApi } from "ag-grid-community";
import { numberValueSetter, stringValueSetter } from "./util";

export type Column =
    | ({ data_type: "string" | "image" | "boolean" | NumberDataType } & ColumnData)
    | ({ data_type: "combobox"; options: { value: any; name: string }[] } & ColumnData);

type ColumnData = {
    id: number;
    name: string;
    tooltip: string;
    key: string;
    index: number;
    width: number;
    is_visible: boolean;
    editable: boolean;
    pinned: boolean;
};

type NumberDataType = (typeof numberDataTypes)[number];

const numberDataTypes = ["float", "int", "dollar", "ruble", "percent"] as const;
function isNumeric(data_type: string): data_type is NumberDataType {
    return numberDataTypes.includes(data_type as any);
}

export async function getColumns(init: {
    onPhotoClicked: (url: string) => void;
    isRowChanged: (row: any) => boolean;
}): Promise<ColDef[]> {
    let columns: Column[] = await (await fetchAuthenticated("settings/columns")).json();
    columns.sort((a, b) => a.index - b.index);
    let colDefs = columns.map(col => {
        let colDef: ColDef = {
            field: col.key,
            headerName: col.name,
            width: col.width,
            editable: col.editable,
            cellClass: cellClass(col.editable, col.data_type),
            wrapHeaderText: true,
            headerTooltip: col.tooltip
        };

        if (col.data_type == "combobox") {
            colDef = {
                ...colDef,
                cellEditor: "agSelectCellEditor",
                cellEditorParams: { values: col.options.map(x => x.value) },
                valueFormatter: ({ value }) => {
                    let name = col.options.find(x => x.value === value)?.name;
                    return name ? name : "N/A";
                }
            };
        } else if (isNumeric(col.data_type)) {
            let _precision = precision(col.data_type);
            let _postfix = postfix(col.data_type);
            colDef = {
                ...colDef,
                cellEditor: "agNumberCellEditor",
                cellEditorParams: {
                    min: 0,
                    precision: _precision,
                    preventStepping: true
                },
                valueFormatter: (params: any) => {
                    if (params.value === null || params.value === undefined) {
                        return "N/A";
                    } else {
                        return `${params.value.toFixed(_precision)}${_postfix}`;
                    }
                },
                valueSetter: numberValueSetter(col.key)
            };
        } else if (col.data_type == "image") {
            colDef = {
                ...colDef,
                cellRenderer: (params: any) =>
                    params.value != null ? `<img src="${params.value}" />` : "",
                onCellClicked: e => {
                    if (e.value) {
                        init.onPhotoClicked(e.value.toString());
                    }
                }
            };
        } else if (col.data_type == "string") {
            colDef.valueSetter = stringValueSetter(col.key);
        } else if (col.data_type == "boolean") {
            // Nothing to do here (agDataGrid handles it automatically).
        }

        if (col.pinned) {
            colDef = {
                ...colDef,
                lockPosition: "left",
                pinned: "left",
                cellClass: e => (init.isRowChanged(e.data!) ? "changed" : [])
            };
        }
        return colDef;
    });

    return colDefs;
}

/** Determines which postfix to use when displaying formatted value of the cell. */
function postfix(data_type: string): string {
    if (data_type == "percent") return "%";
    if (data_type == "dollar") return " $";
    if (data_type == "ruble") return " ₽";
    return "";
}

/** Determines which precision to use for numeric cell. */
function precision(data_type: NumberDataType): number {
    if (data_type == "int") return 0;
    return 2;
}

function cellClass(editable: boolean, data_type: string): string[] {
    let classes = [];
    if (editable) classes.push("editable");
    if (isNumeric(data_type)) classes.push("ag-right-aligned-cell");
    if (data_type == "image") classes.push("product-photo-cell");
    return classes;
}

export async function patchColumns(grid: GridApi) {
    type PatchData = {
        key: string;
        is_visible: true;
        width: number;
        index: number;
    };

    let colDefs = grid.getColumnDefs();
    if (!colDefs) return;
    let patches: PatchData[] = colDefs.map((colDef: ColDef, index) => {
        let column = grid.getColumns()!.find(x => x.getColDef().field == colDef.field)!;
        return {
            key: colDef.field!,
            index,
            is_visible: true,
            width: column.getActualWidth()
        };
    });

    await fetchAuthenticated("settings/columns", {
        method: "PATCH",
        body: JSON.stringify(patches),
        headers: {
            "Content-Type": "application/json"
        }
    });
}
