import type { ColDef, ValueGetterParams, ValueSetterParams } from "ag-grid-community";

export function numberColumnDefinition<T, V = any>(
    field: keyof T,
    init:
        | { kind: "money"; currency: "$" | "₽" }
        | { kind: "percent" }
        | { kind: "number"; precision: number },
    editable: boolean = false
): ColDef<T, V> {
    let postfix = "";
    let precision = 2;
    if (init.kind == "money") {
        postfix = ` ${init.currency}`;
    } else if (init.kind == "percent") {
        postfix = "%";
    } else if (init.kind == "number") {
        precision = init.precision;
    }

    let editable_def = {};
    if (editable) {
        editable_def = {
            cellEditor: "agNumberCellEditor",
            cellEditorParams: {
                min: 0,
                precision,
                preventStepping: true
            },
            type: "editable"
        };
    }

    return {
        ...notNullFieldColumn(field),
        ...notNullNumberFormatter(field, precision, postfix),
        ...editable_def,
        cellClass: "ag-right-aligned-cell"
    };
}

/** Constructs column definition that rejects null or undefined values on set. */
export function notNullFieldColumn<T, V = any>(field: keyof T): ColDef<T> {
    return {
        valueGetter: (params: ValueGetterParams<T, V>) => params.data![field],
        valueSetter: notNullValueSetter<T, V>(field)
    };
}

/** Value setter that rejects null or undefined value. */
export function notNullValueSetter<T, V = any>(field: keyof T) {
    return (params: ValueSetterParams<T, V | null | undefined>) => {
        if (params.newValue === null || params.newValue === undefined) {
            return false;
        } else {
            params.data[field] = params.newValue as any;
            return true;
        }
    };
}

/** Value formatter for numbers that replaces `null` values with "N/A". */
export function notNullNumberFormatter<T, V = any>(
    field: keyof T,
    precision: number = 2,
    postfix: string = ""
): ColDef<T> {
    return {
        valueFormatter: params =>
            params.value === null || params.value === undefined
                ? "N/A"
                : `${params.value.toFixed(precision)}${postfix}`
    };
}
