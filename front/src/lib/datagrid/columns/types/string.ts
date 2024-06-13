import type { ColumnBase } from ".";

export default class StringColumn implements ColumnBase<string> {
    public formatter(val: string | null | undefined) {
        return val ?? "";
    }

    public parser(s: string) {
        return s;
    }
}
