import type { ColDef, ColGroupDef, ColumnGroupShowType, ValueGetterFunc } from "ag-grid-enterprise";
import { numberValueSetter, stringValueSetter } from "./util";

export type ColumnGroup = { header: string; children: Column[] };

export type Column =
    | ({ data_type: "string" | "image" | "boolean" | NumberDataType } & ColumnData)
    | ({ data_type: "combobox"; options: { value: any; name: string }[] } & ColumnData);

type ColumnData = {
    header: string;
    key: string;
    editable?: boolean;
    tooltip?: string;
    pinned?: boolean;
    columnGroupShow?: ColumnGroupShowType;
    cellRenderer?: string;
    valueGetter?: ValueGetterFunc;
};

type NumberDataType = (typeof numberDataTypes)[number];

const numberDataTypes = ["float", "int", "dollar", "ruble", "percent"] as const;
function isNumeric(data_type: string): data_type is NumberDataType {
    return numberDataTypes.includes(data_type as any);
}

export function getColumns(
    columns: (Column | ColumnGroup)[],
    init: {
        onPhotoClicked: (url: string) => void;
        isRowChanged: (row: any) => boolean;
        readonly: boolean;
    }
): ColDef[] {
    let colDefs = columns.map(col => {
        if ("children" in col) {
            return {
                headerName: col.header,
                children: getColumns(col.children, init),
                marryChildren: true
            } satisfies ColGroupDef;
        }

        let editable = init.readonly ? false : col.editable === true;

        let colDef: ColDef = {
            field: col.key,
            headerName: col.header,
            editable,
            cellClass: cellClass(editable, col.data_type),
            wrapHeaderText: true,
            columnGroupShow: col.columnGroupShow,
            headerTooltip: col.tooltip,
            cellRenderer: col.cellRenderer,
            valueGetter: col.valueGetter
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
                cellClass: e => (e.data && init.isRowChanged(e.data) ? "changed" : [])
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
    else if (data_type == "ruble") return 0;
    return 2;
}

function cellClass(editable: boolean, data_type: string): string[] {
    let classes = [];
    if (editable) classes.push("editable");
    if (isNumeric(data_type)) classes.push("ag-right-aligned-cell");
    if (data_type == "image") classes.push("product-photo-cell");
    return classes;
}
