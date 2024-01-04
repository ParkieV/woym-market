import type { ColDef, ValueGetterParams, ValueSetterParams } from "ag-grid-community";

/** Constructs column definition that rejects null or undefined values on set. */
export function notNullFieldColumn<T, V = any>(field: keyof T): ColDef<T> {
    return {
        valueGetter: (params: ValueGetterParams<T, V>) => params.data![field],
        valueSetter: notNullValueSetter<T, V>(field),
    }
}

/** Value setter that rejects null or undefined value. */
export function notNullValueSetter<T, V = any>(field: keyof T) {
    return (params: ValueSetterParams<T, V | null | undefined>) => {
        if (params.newValue === null || params.newValue === undefined)
        {
            return false;
        }
        else
        {
            let x = params.data[field];
            let y = params.newValue;
            let xa = params.data[field];
            params.data[field] = params.newValue as any;
            return true;
        }
    }
}
