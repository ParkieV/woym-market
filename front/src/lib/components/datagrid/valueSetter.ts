import type { ValueSetterFunc } from "ag-grid-enterprise";

export function valueSetter<T extends Object>(field: string) {
    return (({ data, oldValue, newValue }) => {
        if (newValue instanceof Error) return false;
        if (typeof oldValue === "string" && newValue === null) {
            setByPath(data, "", field);
            return true;
        }

        if (newValue === null || newValue === undefined) {
            return false;
        }
        if (typeof newValue === "number" && !Number.isFinite(newValue)) {
            return false;
        }

        // FIXME: won't handle fields with dots correctly
        setByPath(data, newValue, field);
        return true;
    }) as ValueSetterFunc<any, T>;
}

function setByPath(data: any, value: any, path: string) {
    let fields = path.split(".");
    for (let i = 0; i < fields.length - 1; i++) {
        data = data[fields[i]];
    }
    data[fields[fields.length - 1]] = value;
}
