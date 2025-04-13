import { ChangeList } from "$lib/datagrid/plugins/changes";
import { get, writable, type Writable } from "svelte/store";
import { setLocalUpdateTime, shouldReload } from "./data/settings";

/** Managed state of the grid5. */
export class GridState<T, K> implements Writable<T[]> {
    constructor(public getter: () => T[] | Promise<T[]>) {
        shouldReload.subscribe(async should => {
            if (!should || !this.initialized) return;
            this.initial = await this.getter();
            this.current.set(structuredClone(this.initial));
            setLocalUpdateTime();
        });
    }

    private _initialized = false;
    public get initialized() {
        return this._initialized;
    }

    /** Editable copy of initially loaded data. */
    private current: Writable<T[]> = writable([]);

    /** Initially loaded data. */
    private initial: T[] = [];

    public subscribe = this.current.subscribe;
    public set = this.current.set;
    public update = this.current.update;

    /** Changelist to track what values were changed. */
    public changes = new ChangeList<T, K>();

    /** Initially loads data if it wasn't loaded yet. */
    public async load() {
        if (!this.initialized) {
            this.forceReload();
        }
    }

    /** Forcefully loads or reloads data. */
    public async forceReload() {
        this.changes.clear();
        this.initial = await this.getter();
        this.current.set(structuredClone(this.initial));
        this._initialized = true;
    }

    /** Resets changes applied to the data. */
    public cancel() {
        this.changes.clear();
        this.current.set(structuredClone(this.initial));
    }
    public apply() {
        this.current.set(structuredClone(this.initial));
        this.changes.clear();
    }
    public apply() {
        this.initial = structuredClone(get(this.current));
        this.changes.clear();
    }

    /** Cancels changes and marks state as unloaded. */
    public reset() {
        this.cancel();
        this._initialized = false;
    }
}
