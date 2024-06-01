import type { ColDef, ColGroupDef, ColumnGroupShowType, ValueGetterFunc } from "ag-grid-enterprise";
import type { ColumnBase } from "./types";
import valueSetter from "./valueSetter";
import ImageColumn from "./types/image";

export type ColumnGroup = { header: string; children: Column[] };

export type Column = {
    base: ColumnBase<any>;
    header: string;
    key: string;
    editable?: boolean;
    tooltip?: string;
    pinned?: boolean;
    columnGroupShow?: ColumnGroupShowType;
    valueGetter?: ValueGetterFunc;
};

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
            cellClass: cellClass(col.base, editable),
            wrapHeaderText: true,
            columnGroupShow: col.columnGroupShow,
            headerTooltip: col.tooltip,
            valueGetter: col.valueGetter
        };

        const { parser, formatter } = col.base;
        const valueParser = parser
            ? ({ newValue }: { newValue: string }) => parser.bind(col.base)(newValue)
            : undefined;
        const valueFormatter = formatter
            ? ({ value }: { value: any }) => formatter.bind(col.base)(value)
            : undefined;

        colDef = {
            ...colDef,
            cellRenderer: col.base.cellRenderer,
            cellEditor: col.base.cellEditor,
            cellEditorParams: col.base.cellEditorParams,
            valueParser,
            valueFormatter,
            valueSetter: valueSetter(col.key)
        };

        if (col.base instanceof ImageColumn) {
            colDef.onCellClicked = e => {
                if (e.value) {
                    init.onPhotoClicked(e.value.toString());
                }
            };
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

function cellClass(ops: ColumnBase<any>, editable: boolean): string[] {
    let classes = ops.classes?.() ?? [];
    if (editable) classes.push("editable");
    return classes;
}
