import type { CellValueChangedEvent } from "ag-grid-enterprise";
import type { GridPlugin } from ".";
import type { MyGridOptions } from "..";
import { derived, get, writable, type Readable, type Writable } from "svelte/store";

/**
 * Modifies provided grid options to enable change monitoring.
 *
 * Changed cells will have `changed` class applied.
 * */
export default class ChangesPlugin<T, K extends keyof T> implements GridPlugin<T> {
    constructor(
        private key: K,
        private changes: ChangeList<T, K>,
        private onChange?: (e: CellValueChangedEvent<T, K>) => void | Promise<void>
    ) {}

    init(opts: MyGridOptions<T>): void | Promise<void> {
        for (const col of opts.columnDefs) {
            if (!("children" in col)) {
                if (col.pinned) {
                    if (col.cellClassRules === undefined) {
                        col.cellClassRules = {};
                    }
                    col.cellClassRules.changed = ({ data }) => {
                        if (!data) return false;
                        return get(this.changes).isChanged(data[this.key]);
                    };
                }
            }
        }

        let func = opts.onCellValueChanged;
        opts.onCellValueChanged = e => {
            this.changes.add(e.data[this.key]);
            e.api.refreshCells({ rowNodes: [e.node] });
            this.onChange?.(e);
            func?.(e);
        };
    }
}

// TODO: check which properties were changed.
export class ChangeList<T, KEY extends keyof T> implements Readable<ChangeListInfo<T[KEY]>> {
    private changes: Writable<Set<T[KEY]>> = writable(new Set());

    /** Mark value with key as changed. */
    public add(key: T[KEY]) {
        this.changes.update(x => (x.add(key), x));
    }

    /** Reset list of changes. */
    public clear() {
        this.changes.update(x => (x.clear(), x));
    }

    public subscribe = derived([this.changes], ([changes]) => new ChangeListInfo(changes))
        .subscribe;
}

export class ChangeListInfo<V> {
    constructor(private changes: Set<V>) {}

    /** Returns `true` if entry with provided key has any changes. */
    public isChanged(key: V): boolean {
        return this.changes.has(key);
    }

    /** Returns `true` if any changes were applied. */
    public get hasChanges(): boolean {
        return this.changes.size !== 0;
    }

    /** Returns number of changed offers. */
    public get count(): number {
        return this.changes.size;
    }
}
