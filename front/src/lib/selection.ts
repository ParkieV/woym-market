import { derived, writable, type Readable, type Writable } from "svelte/store";
import type { Filter } from "./datagrid/filters";

export class Selection<T, K> {
    constructor(filter: Readable<Filter<T>>) {
        this.selected = writable(new Map());
        this.filter = filter;
        this.filtered = derived([this.filter, this.selected], ([filter, selected]) => {
            return new Map([...selected].filter(([_, val]) => filter(val)));
        });
    }

    public readonly selected: Writable<Map<K, T>>;
    public readonly filter: Readable<Filter<T>>;
    public readonly filtered: Readable<Map<K, T>>;
}
