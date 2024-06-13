<script lang="ts">
    import {
        fetchFboStocks,
        patchFboStocks,
        type FboStocks,
        type FboStorage
    } from "$lib/data/fbo_storage";
    import Footer from "../Footer.svelte";
    import { getContext, onMount, setContext } from "svelte";
    import Grid from "$lib/grid/Grid.svelte";
    import { writable, type Writable } from "svelte/store";
    import type { GridDefinition } from "$lib/datagrid";
    import ImageWindow from "$lib/components/windows/ImageWindow.svelte";
    import fboOffersGrid from "./fbo-offer";
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

    export let data: PageData;
    let stocks: FboStocks[] = [];

    let changes = new ChangeList<FboStocks, "id">();
    let innerChanges = new ChangeList<FboStorage, "id">();

    let selected_image: string | undefined = undefined;

    async function refreshData() {
        changes.clear();
        changes = changes;
        innerChanges.clear();
        innerChanges = innerChanges;
        stocks = await fetchFboStocks();
    }

    async function save() {
        let ok = await patchFboStocks(stocks.filter(x => changes.isChanged(x.id)));
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
                        changes.add(stock.id);
                        changes = changes;
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

        return fboOffersGrid(changes, innerChanges)
            .plugin(new FilterPlugin(filterStore))
            .plugin(new StatePlugin("fbo_storage"))
            .plugin(new ChangesPlugin("id", changes))
            .plugin(new ReadonlyPlugin(!$userCanModify))
            .plugin(new ZoomPlugin(href => (selected_image = href)))
            .plugin(new ClassesPlugin())
            .plugin(new RowSelectionPlugin(selectedStocks))
            .plugin(new DetailGridPlugin(detail, data => data.stocks));
    })();
</script>

{#if selected_image}
    <ImageWindow bind:src={selected_image} />
{/if}

<Toolbar bind:filter bind:storage_filter markets={data.options} />
{#if browser}
    <Grid {definition} bind:data={stocks} />
{/if}
<Footer bind:changes on:reload={refreshData} on:save={save} />
