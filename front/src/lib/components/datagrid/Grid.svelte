<script lang="ts" generics="T, K extends keyof T">
    import { getState as getGridState, gridStateSources, setState as setGridState } from "./state";
    import { userCanModify } from "$lib/data/user";
    import ImageWindow from "$lib/components/windows/ImageWindow.svelte";
    import { getColumns, type Column, type ColumnGroup } from "./columns";
    import { ChangeList } from "$lib/components/datagrid/changes";
    import { createGrid, type ColDef, type GridApi, type GridOptions } from "ag-grid-enterprise";
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
    /** Unmanaged grid options to apply. Managed fields will be overwritten. */
    export let otherGridOptions: GridOptions = {};

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
            },
            readonly: !$userCanModify
        });

        const initialState = await getGridState(grid_name);
        const options: GridOptions<T> = {
            ...otherGridOptions,
            columnDefs,
            suppressDragLeaveHidesColumns: true,
            rowHeight: 75,
            onCellValueChanged: e => {
                changes.add(e.data[key]);
                changes = changes;
                e.api.redrawRows({ rowNodes: [e.node] });
            },
            tooltipShowDelay: 500,
            onStateUpdated: ({ state, sources }) => {
                for (const source of gridStateSources) {
                    if (sources.includes(source)) {
                        setGridState(grid_name, state);
                        break;
                    }
                }
            },
            enableRangeSelection: true,
            enableRangeHandle: true,
            getContextMenuItems: () => ["cut", "copy", "paste"],
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
