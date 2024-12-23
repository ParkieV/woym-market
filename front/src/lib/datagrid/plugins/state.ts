import { fetchPlain } from "$lib/fetch";
import type { GridState as AgGridState } from "ag-grid-enterprise";
import type { GridPlugin } from ".";
import type { MyGridOptions } from "..";

/** Preserves grid state in LocalStorage and remote server. */
export default class StatePlugin<T> implements GridPlugin<T> {
    constructor(private key: string) {}

    async init(opts: MyGridOptions<T>): Promise<void> {
        let func = opts.onStateUpdated;
        opts.onStateUpdated = arg => {
            for (const source of gridStateSources) {
                if (arg.sources.includes(source)) {
                    setState(this.key, arg.state);
                    break;
                }
            }
            func?.(arg);
        };
        opts.initialState = await getState(this.key);
    }
}

const gridStateSources: (keyof AgGridState)[] = [
    "columnOrder",
    "columnGroup",
    "columnPinning",
    "columnSizing",
    "sort"
];

async function getState(gridName: string): Promise<AgGridState> {
    let local = getLocal(gridName);
    let remote = await getRemote(gridName);

    if (remote === null || remote.data === null) remote = { updated_at: new Date(0), data: null };
    if (local === null || local.data === null) local = { updated_at: new Date(0), data: null };

    if (local.updated_at > remote.updated_at) {
        return local.data ?? {};
    } else {
        setLocal(gridName, new GridState(remote.data));
        return remote.data ?? {};
    }
}

async function setState(gridName: string, state: AgGridState) {
    let _state: GridState = new GridState(state);
    setLocal(gridName, _state);
    scheduleSetRemote(gridName, _state);
}

class GridState {
    public updated_at: Date;
    public data: AgGridState | null;

    public static fromString(s: string): GridState {
        let json: { updated_at: string; data: string } = JSON.parse(s);
        const state: GridState = {
            updated_at: new Date(json.updated_at),
            data: JSON.parse(json.data)
        };
        return state;
    }

    public toString(): string {
        let data: string;
        if (this.data) {
            let { columnOrder, columnGroup, columnPinning, columnSizing, sort } = this.data;
            data = JSON.stringify({
                columnOrder,
                columnGroup,
                columnPinning,
                columnSizing,
                sort
            });
        } else {
            data = "null";
        }
        const intermediate: { data: string; updated_at: string } = {
            data,
            updated_at: this.updated_at.toISOString()
        };

        return JSON.stringify(intermediate);
    }

    public constructor(data: AgGridState | null, updated_at?: Date) {
        this.updated_at = updated_at ?? new Date();
        this.data = data;
    }
}

function getLocal(gridName: string): GridState | null {
    const item = localStorage.getItem(key(gridName));
    if (item === null) return null;

    try {
        return GridState.fromString(item);
    } catch {
        let state = { updated_at: new Date(), data: {} };
        setLocal(gridName, state);
        return state;
    }
}

async function getRemote(gridName: string): Promise<GridState | null> {
    const response = await fetchPlain(`/settings/tables/${gridName}`);
    const string = await response.text();
    if (string === "null") return null;
    try {
        return GridState.fromString(string);
    } catch {
        return null;
    }
}

function setLocal(gridName: string, state: GridState) {
    localStorage.setItem(key(gridName), state.toString());
}

async function setRemote(gridName: string, state: GridState) {
    await fetchPlain(`/settings/tables/${gridName}`, {
        method: "PATCH",
        body: state.toString(),
        headers: {
            "Content-Type": "application/json"
        }
    });
}

let plannedRemoteUpdate: GridState | undefined = undefined;
function scheduleSetRemote(gridName: string, state: GridState) {
    if (!plannedRemoteUpdate) {
        setTimeout(async () => {
            if (plannedRemoteUpdate) {
                await setRemote(gridName, plannedRemoteUpdate);
                plannedRemoteUpdate = undefined;
            }
        }, 2000);
    }
    plannedRemoteUpdate = state;
}

const key = (gridName: string) => `gridState-${gridName}`;
