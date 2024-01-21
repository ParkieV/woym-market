<script lang="ts">
    import type { Offer, OffersData } from "$lib/data/offers";
    import { ChangeList } from "$lib/datagrid/changes";
    import { DataGridOptions } from "$lib/datagrid/offers";
    import { createGrid, type GridApi } from "ag-grid-community";
    import { createEventDispatcher, onMount } from "svelte";

    export let data: OffersData;
    export let changes: ChangeList<Offer, "sku">;

    let grid: GridApi;
    $: if (grid && data.offers.length != 0) {
        grid.setGridOption("rowData", data.offers);
    } else if (grid) {
        grid.showLoadingOverlay();
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
                changes.add(offer.sku);
                changes = changes;
            },
            isOfferChanged: sku => changes.isChanged(sku)
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
