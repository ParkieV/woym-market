import type {
    ColDef,
    ColDefField,
    ColGroupDef,
    ColumnGroupShowType,
    ValueGetterFunc
} from "ag-grid-enterprise";
import type { ColumnBase } from "./columns/types";
import valueSetter from "./columns/valueSetter";

export type ColumnGroup = { header: string; children: Column[] };

export type Column<T = any> = {
    base: ColumnBase<T>;
    header: string;
    key: string;
    editable?: boolean;
    tooltip?: string;
    pinned?: boolean;
    selectionCheckbox?: boolean;
    columnGroupShow?: ColumnGroupShowType;
    valueGetter?: ValueGetterFunc;
};

/** {@link ColDef} with preserved translation source. */
export type MyColDef<T = any> = ColDef<T> & {
    source: Column;
};

/** {@link ColGroupDef} with preserved translation source. */
export type MyColGroupDef<T = any> = ColGroupDef<T> & {
    source: ColumnGroup;
    children: (MyColDef<T> | MyColGroupDef<T>)[];
};

export function getColumns<T>(
    columns: (Column<T> | ColumnGroup)[]
): (MyColDef<T> | MyColGroupDef<T>)[] {
    let colDefs = columns.map(col => {
        if ("children" in col) {
            return {
                headerName: col.header,
                children: getColumns<T>(col.children),
                source: col,
                marryChildren: true
            } satisfies MyColGroupDef<T>;
        }

        let editable = col.editable === true;

        let colDef: MyColDef<T> = {
            source: col,
            field: col.key as ColDefField<T>,
            headerName: col.header,
            editable,
            cellClass: col.base.classes,
            valueGetter: col.valueGetter,
            wrapHeaderText: true,
            columnGroupShow: col.columnGroupShow,
            headerTooltip: col.tooltip,

            checkboxSelection: col.selectionCheckbox,
            headerCheckboxSelection: col.selectionCheckbox,
            headerCheckboxSelectionFilteredOnly: true
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

        if (col.pinned) {
            colDef = {
                ...colDef,
                lockPosition: "left",
                pinned: "left"
            };
        }
        return colDef;
    });

    return colDefs;
}
