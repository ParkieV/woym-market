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
