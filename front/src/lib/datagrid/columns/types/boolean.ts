import type { ColumnBase } from ".";

export default class BooleanColumn implements ColumnBase<boolean> {
    cellRenderer = "agCheckboxCellRenderer";
    cellEditor = "agCheckboxCellEditor";

    formatter(val: boolean | null | undefined) {
        if (val === true) return "true";
        if (val === false) return "false";
        return "";
    }
    parser(s: string) {
        s = s.trim().toLowerCase();
        if (s === "true" || s === "да" || s === "+" || s === "1") {
            return true;
        }
        if (s === "false" || s === "нет" || s === "-" || s === "0") {
            return false;
        }
        return new Error();
    }
}
