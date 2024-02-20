import type { ColDef, ValueSetterParams } from "ag-grid-enterprise";

export function numberValueSetter(field: string) {
    return (params: ValueSetterParams<any, number | null | undefined>) => {
        if (params.newValue === null || params.newValue === undefined) {
            return false;
        } else {
            // FIXME: won't handle fields with dots correctly
            setByPath(params.data, params.newValue, field);
            return true;
        }
    };
}

export function stringValueSetter(field: string) {
    return (params: ValueSetterParams<any, string | null | undefined>) => {
        let value = params.newValue;
        if (params.newValue === null || params.newValue === undefined) {
            value = "";
        }
        // FIXME: won't handle fields with dots correctly
        setByPath(params.data, value, field);
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

function setByPath(data: any, value: any, path: string) {
    let fields = path.split(".");
    for (let i = 0; i < fields.length - 1; i++) {
        data = data[fields[i]];
    }
    data[fields[fields.length - 1]] = value;
}
