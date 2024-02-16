import type { GridState } from "ag-grid-enterprise";

export function getGridState(grid_name: string): GridState | undefined {
    const key = getLocalStorageKey(grid_name);

    const value = localStorage.getItem(key);
    if (value === null) return undefined;

    return JSON.parse(value);
}

export function setGridState(grid_name: string, state: GridState) {
    const key = getLocalStorageKey(grid_name);

    let { columnOrder, columnGroup, columnPinning, columnSizing, sort } = state;
    let value = JSON.stringify({
        columnOrder,
        columnGroup,
        columnPinning,
        columnSizing,
        sort
    });

    localStorage.setItem(key, value);
}

function getLocalStorageKey(grid_name: string) {
    return `gridState-${grid_name}`;
}
