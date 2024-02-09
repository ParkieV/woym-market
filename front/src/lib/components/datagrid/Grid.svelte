<script lang="ts" generics="T, K extends keyof T">
    import ImageWindow from "$lib/components/windows/ImageWindow.svelte";
    import { getColumns, type Column, type ColumnGroup } from "./columns";
    import { ChangeList } from "$lib/components/datagrid/changes";
    import { createGrid, type ColDef, type GridApi, type GridOptions } from "ag-grid-community";
    import { onMount } from "svelte";

    /** Name of the grid that is used as key to preserve order of columns, etc. */
    export let grid_name: string;
    /** Data to display in the table. */
    export let data: T[];
    /** Field name in the data that is used as key. */
    export let key: K;
    /** Tracker of changed entries. */
    export let changes: ChangeList<T, K>;
    /** Filter function for rows. */
    export let filter: (value: T) => boolean = () => true;
    /** List of column definitions (in custom format). */
    export let columns: (Column | ColumnGroup)[];

    $: if (grid) {
        filter;
        grid.setGridOption("doesExternalFilterPass", e => filter(e.data!));
        grid.setGridOption("isExternalFilterPresent", () => true);
        grid.onFilterChanged();
    }

    let selected_image: string | undefined = undefined;

    let grid: GridApi;
    $: if (grid && data.length != 0) {
        grid.setGridOption("rowData", data);
    } else if (grid) {
        grid.showLoadingOverlay();
    }

    onMount(async () => {
        const columnDefs: ColDef<T>[] = getColumns(columns, {
            onPhotoClicked: url => (selected_image = url),
            isRowChanged: (value: T) => {
                return changes.isChanged(value[key]);
            }
        });

        const stateKey = `gridState-${grid_name}}`;
        const _initialState = localStorage.getItem(stateKey);
        const initialState = _initialState ? JSON.parse(_initialState) : undefined;

        const options: GridOptions<T> = {
            columnDefs,
            suppressDragLeaveHidesColumns: true,
            rowHeight: 75,
            onCellValueChanged: e => {
                changes.add(e.data[key]);
                changes = changes;
                e.api.redrawRows({ rowNodes: [e.node] });
            },
            tooltipShowDelay: 500,
            onStateUpdated: ({ state }) => {
                let { columnOrder, columnGroup, columnPinning, columnSizing, sort } = state;
                let _state = { columnOrder, columnGroup, columnPinning, columnSizing, sort };
                localStorage.setItem(stateKey, JSON.stringify(_state));
            },
            initialState
        };

        grid = createGrid(element, options);
    });

    let element: HTMLElement;
</script>

{#if selected_image}
    <ImageWindow bind:src={selected_image} />
{/if}
<div bind:this={element} class="ag-theme-quartz"></div>

<style lang="scss">
    div {
        flex: 1;
        height: 100%;
    }
</style>
