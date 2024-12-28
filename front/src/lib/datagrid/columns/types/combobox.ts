import type { ColumnBase } from ".";

export default class ComboboxColumn<V extends string | number | null>
    implements ColumnBase<ComboboxOption<V>>
{
    cellEditor = "agRichSelectCellEditor";
    cellEditorParams: any;

    constructor(private values: ComboboxOptionsSetter<V>) {
        this.cellEditorParams = (params: any) => {
            if (typeof this.values === "function") return { values: this.values(params) };
            return { values: this.values };
        };
    }

    public formatter(val: ComboboxOption<V> | null | undefined) {
        if (val === null || val === undefined) return "N/A";
        return val.name;
    }

    public parser(_s: string): never {
        throw new Error("Parser should not be used in combobox column");
    }
}

type ComboboxOptionsSetter<V extends string | number | null> =
    | ComboboxOption<V>[]
    | ((params: any) => ComboboxOption<V>[]);

type ComboboxOption<V extends string | number | null> = { name: string; value: V };
