<script lang="ts" generics="T, K extends keyof T">
    import ImageWindow from "$lib/components/windows/ImageWindow.svelte";
    import { getColumns, patchColumns } from "./columns";
    import { ChangeList } from "$lib/components/datagrid/changes";
    import { createGrid, type ColDef, type GridApi, type GridOptions } from "ag-grid-community";
    import { onMount } from "svelte";

    /** Data to display in the table. */
    export let data: T[];
    /** Field name in the data that is used as key. */
    export let key: K;
    /** Tracker of changed entries. */
    export let changes: ChangeList<T, K>;

    let selected_image: string | undefined = undefined;

    let grid: GridApi;
    $: if (grid && data.length != 0) {
        grid.setGridOption("rowData", data);
    } else if (grid) {
        grid.showLoadingOverlay();
    }

    export let filter: (value: T) => boolean;
    $: if (grid) {
        filter;
        grid.setGridOption("doesExternalFilterPass", e => filter(e.data!));
        grid.setGridOption("isExternalFilterPresent", () => true);
        grid.onFilterChanged();
    }

    onMount(async () => {
        const columnDefs: ColDef<T>[] = await getColumns({
            onPhotoClicked: url => (selected_image = url),
            isRowChanged: (value: T) => {
                return changes.isChanged(value[key]);
            }
        });

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
            onColumnResized: e => patchColumns(e.api),
            onColumnMoved: e => patchColumns(e.api)
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
