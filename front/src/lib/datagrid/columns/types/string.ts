import type { ColumnBase } from ".";
import type { MyColDef } from "$lib/datagrid/columns";

export default class StringColumn implements ColumnBase<any> {
    constructor(public editor?: TextEditor) {}

    public apply(col: MyColDef<any>) {
        if (this.editor === undefined) {
            col.cellEditor = "agTextCellEditor";
            return;
        }
        let { kind: cellEditor, ...params } = this.editor;
        col.cellEditor = cellEditor;
        col.cellEditorPopup = cellEditor === "agTextCellEditor";
        col.cellEditorParams = params;
    }

    public formatter(val: string | null | undefined) {
        return val ?? "";
    }

    public parser(s: string) {
        return s;
    }
}

export type TextEditor =
    | { kind: "agTextCellEditor"; maxLength: number }
    | { kind: "agLargeTextCellEditor"; rows: number; cols: number; maxLength?: number };
