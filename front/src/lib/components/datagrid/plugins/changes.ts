import type { GridDefinition, GridPlugin } from "..";

/**
 * Modifies provided grid options to enable change monitoring.
 *
 * Changed cells will have `changed` class applied.
 * */
export default function ChangesPlugin<T, K extends keyof T>(
    key: K,
    changes: ChangeList<T, K>
): GridPlugin {
    return ({ options: opts }) => {
        for (const col of opts.columnDefs) {
            if (!("children" in col)) {
                if (col.pinned) {
                    if (col.cellClassRules === undefined) {
                        col.cellClassRules = {};
                    }
                    col.cellClassRules.changed = ({ data }) => {
                        if (!data) return false;
                        return changes.isChanged(data[key]);
                    };
                }
            }
        }
        opts.onCellValueChanged = e => {
            changes.add(e.data[key]);
            e.api.refreshCells({ rowNodes: [e.node] });
        };
    };
}

// TODO: check which properties were changed.
export class ChangeList<T, KEY extends keyof T> {
    private changes: Set<T[KEY]> = new Set();

    /** Mark value with key as changed. */
    public add(key: T[KEY]) {
        this.changes.add(key);
    }

    /** Returns `true` if entry with provided key has any changes. */
    public isChanged(key: T[KEY]): boolean {
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

    /** Reset list of changes. */
    public clear() {
        this.changes.clear();
    }
}
