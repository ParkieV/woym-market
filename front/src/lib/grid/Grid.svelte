<script lang="ts" generics="T">
    import type { GridDefinition } from "$lib/datagrid";
    import { type GridApi } from "ag-grid-enterprise";
    import { onMount } from "svelte";

    /** Grid definition. */
    export let definition: GridDefinition<T>;

    /** Data to display in the table. */
    export let data: T[];

    let grid: GridApi;
    $: if (grid && data.length != 0) {
        grid.setGridOption("rowData", data);
    } else if (grid) {
        grid.showLoadingOverlay();
    }

    onMount(async () => {
        grid = await definition.build(element);
    });

    let element: HTMLElement;
</script>

<div bind:this={element} class="ag-theme-quartz"></div>

<style lang="scss">
    div {
        flex: 1;
        height: 100%;
    }
</style>
