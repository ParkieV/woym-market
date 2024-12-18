export default function createSearchFilter<T>(search: string, getters: readonly FieldGetter<T>[]) {
    search = normalizeString(search);
    return (data: T) => {
        let strings = getters.map(getter =>
            typeof getter === "string" ? data[getter] + "" : getter(data)
        );
        return strings
            .filter(data => data !== undefined && data !== null)
            .map(data => normalizeString((data as {}).toString()))
            .some(s => s.includes(search));
    };
}
function normalizeString(s: string): string {
    return s.trim().toLowerCase().replaceAll("ё", "е");
}
export type FieldGetter<T> = (keyof T & string) | ((data: T) => string | string[]);
