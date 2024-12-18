import type { ColumnBase } from ".";

export default class ComboboxColumn<V extends string | number> implements ColumnBase<V> {
    options: { name: string; value: V }[];

    cellEditor: string;
    cellEditorParams: any;

    formatter(val: V | null | undefined) {
        if (val === null || val === undefined) return "N/A";
        return this.options.find(x => x.value === val)?.name ?? "???";
    }

    parser(s: string) {
        s = s.trim();
        if (!this.options.map(x => x.value).includes(s as V)) {
            return new Error();
        }

        const type = typeof this.options[0].value;
        if (type === "number") {
            return Number(s) as V;
        } else if (type === "string") {
            return s as V;
        } else {
            return new Error();
        }
    }

    constructor(options: { name: string; value: V }[]) {
        this.options = options;
        this.cellEditor = "agSelectCellEditor";
        this.cellEditorParams = { values: this.options.map(x => x.value) };
    }
}
