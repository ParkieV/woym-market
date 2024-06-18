<script lang="ts">
    import {
        fetchFboStocks,
        patchFboStocks,
        type FboStocks,
        type FboStorage
    } from "$lib/data/fbo_storage";
    import Footer from "../Footer.svelte";
    import { getContext, onMount } from "svelte";
    import Grid from "$lib/grid/Grid.svelte";
    import { writable, type Writable } from "svelte/store";
    import ImageWindow from "$lib/components/windows/ImageWindow.svelte";
    import fboOffersGrid, { calcStocksToDeliver } from "./fbo-offer";
    import { userCanModify } from "$lib/data/user";
    import type { Filter } from "$lib/datagrid/filters";
    import Toolbar from "./Toolbar.svelte";
    import type { PageData } from "./$types";
    import fboWarehouseGrid from "./fbo-warehouse";
    import { browser } from "$app/environment";
    import { selectedStocks, selectedStorage } from "./selected";

    import ChangesPlugin, { ChangeList } from "$lib/datagrid/plugins/changes";
    import StatePlugin from "$lib/datagrid/plugins/state";
    import ReadonlyPlugin from "$lib/datagrid/plugins/readonly";
    import ZoomPlugin from "$lib/datagrid/plugins/zoom";
    import ClassesPlugin from "$lib/datagrid/plugins/classes";
    import RowSelectionPlugin from "$lib/datagrid/plugins/row-selection";
    import DetailGridPlugin from "$lib/datagrid/plugins/detail";
    import FilterPlugin from "$lib/datagrid/plugins/filter";
    import { SummaryPlugin } from "$lib/datagrid/plugins/summary";

    export let data: PageData;
    let stocks: FboStocks[] = [];

    let changes = writable(new ChangeList<FboStocks, "id">());
    let innerChanges = writable(new ChangeList<FboStorage, "id">());

    let selected_image: string | undefined = undefined;

    async function refreshData() {
        $changes.clear();
        $changes = $changes;
        $innerChanges.clear();
        $innerChanges = $innerChanges;
        stocks = await fetchFboStocks();
    }

    async function save() {
        let ok = await patchFboStocks(stocks.filter(x => $changes.isChanged(x.id)));
        if (ok) await refreshData();
    }

    let refresh = getContext<Writable<() => {}>>("refresh");
    $refresh = refreshData;

    onMount(async () => (stocks = await fetchFboStocks()));

    let filter: Filter<FboStocks>;
    let filterStore = writable<Filter<FboStocks>>();
    $: $filterStore = filter;

    let storage_filter: Filter<FboStorage>;
    let storageFilterStore = writable<Filter<FboStorage>>();
    $: $storageFilterStore = storage_filter;

    const definition = (() => {
        const detail = fboWarehouseGrid()
            .plugin(new FilterPlugin(storageFilterStore))
            .plugin(
                new ChangesPlugin("id", innerChanges, ({ data }) => {
                    let stock = stocks.find(x => x.stocks.some(s => s.id === data.id));
                    if (stock) {
                        $changes.add(stock.id);
                        $changes = $changes;
                    }
                })
            )
            .plugin(new ReadonlyPlugin(!$userCanModify))
            .plugin(new ClassesPlugin())
            .plugin(
                new RowSelectionPlugin(selectedStorage, {
                    key: ({ warehouse }) => warehouse.id,
                    sync: true
                })
            );

        const master = fboOffersGrid(changes, innerChanges)
            .plugin(new FilterPlugin(filterStore))
            .plugin(new StatePlugin("fbo_storage"))
            .plugin(new ChangesPlugin("id", changes))
            .plugin(new ReadonlyPlugin(!$userCanModify))
            .plugin(new ZoomPlugin(href => (selected_image = href)))
            .plugin(new ClassesPlugin())
            .plugin(new RowSelectionPlugin(selectedStocks))
            .plugin(new DetailGridPlugin(detail, data => data.stocks))
            .plugin(
                new SummaryPlugin<FboStocks>({
                    sku: () => "Итого",
                    volume: ({ rows }) =>
                        rows.reduce((sum, row) => sum + row.volume * calcStocksToDeliver(row), 0),
                    self_weight: ({ rows }) =>
                        rows.reduce(
                            (sum, row) => sum + row.self_weight * calcStocksToDeliver(row),
                            0
                        ),
                    cost_price: ({ rows }) =>
                        rows.reduce(
                            (sum, row) => sum + row.cost_price * calcStocksToDeliver(row),
                            0
                        ),
                    profit: ({ rows }) =>
                        rows.reduce((sum, row) => sum + row.profit * calcStocksToDeliver(row), 0)
                })
            );
        return master;
    })();
</script>

{#if selected_image}
    <ImageWindow bind:src={selected_image} />
{/if}

<Toolbar bind:filter bind:storage_filter markets={data.options} />
{#if browser}
    <Grid {definition} bind:data={stocks} />
{/if}
<Footer bind:changes={$changes} on:reload={refreshData} on:save={save} />
