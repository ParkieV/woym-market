import type { ValueSetterFunc } from "ag-grid-enterprise";

export default function valueSetter<T extends Object>(field: string, setter?: ValueSetterFunc) {
    return (params => {
        let { data, oldValue, newValue } = params;
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

        if (setter) return setter(params);
        else {
            // FIXME: won't handle fields with dots correctly
            setByPath(data, newValue, field);
            return true;
        }
    }) as ValueSetterFunc<any, T>;
}

function setByPath(data: any, value: any, path: string) {
    let fields = path.split(".");
    for (let i = 0; i < fields.length - 1; i++) {
        data = data[fields[i]];
    }
    data[fields[fields.length - 1]] = value;
}
