import type { ColDef, ValueSetterParams } from "ag-grid-enterprise";

export function numberValueSetter(field: string) {
    return (params: ValueSetterParams<any, number | null | undefined>) => {
        if (params.newValue === null || params.newValue === undefined) {
            return false;
        } else {
            params.data[field] = params.newValue as any;
            return true;
        }
    };
}

export function stringValueSetter(field: string) {
    return (params: ValueSetterParams<any, string | null | undefined>) => {
        if (params.newValue === null || params.newValue === undefined) {
            params.data[field] = "";
        } else {
            params.data[field] = params.newValue as any;
        }
        return true;
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
