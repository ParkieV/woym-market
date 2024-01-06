<script lang="ts">
    import type { Offer } from "$lib";
    import { DataGridOptions } from "$lib/datagrid/offers";
    import { createGrid, type GridApi } from "ag-grid-community";
    import { createEventDispatcher, onMount } from "svelte";

    export let data: "loading" | Offer[];
    export let changed: Map<string, Offer> = new Map();

    let grid: GridApi;
    $: if (grid && data == "loading") {
        grid.showLoadingOverlay();
    } else if (grid && typeof data == "object") {
        grid.setGridOption("rowData", data);
    }

    export let search: string;
    $: if (grid) {
        search;
        grid.onFilterChanged();
    }

    let dispatch = createEventDispatcher<{ photoClicked: string }>();
    onMount(() => {
        const gridElement = document.querySelector("#grid")! as HTMLElement;
        const options = DataGridOptions({
            search: () => search,
            onPhotoClicked: src => dispatch("photoClicked", src),
            onOfferChanged: offer => {
                changed.set(offer.sku, offer);
                changed = changed;
            },
            isOfferChanged: sku => changed.has(sku)
        });
        grid = createGrid(gridElement, options);
    });
</script>

<div id="grid" class="ag-theme-quartz"></div>

<style lang="scss">
    #grid {
        flex: 1;
        height: 100%;
    }
</style>
