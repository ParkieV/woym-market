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

    import ChangesPlugin, { ChangeList } from "$lib/datagrid/plugins/changes";
    import StatePlugin from "$lib/datagrid/plugins/state";
    import ReadonlyPlugin from "$lib/datagrid/plugins/readonly";
    import ZoomPlugin from "$lib/datagrid/plugins/zoom";
    import ClassesPlugin from "$lib/datagrid/plugins/classes";
    import RowSelectionPlugin from "$lib/datagrid/plugins/row-selection";
    import DetailGridPlugin from "$lib/datagrid/plugins/detail";

    export let data: PageData;

    let definition: GridDefinition;
    let stocks: FboStocks[] = [];

    let changes = new ChangeList<FboStocks, "id">();
    let innerChanges = new ChangeList<FboStorage, "id">();

    let selected_image: string | undefined = undefined;

    let selectedStocks = writable(new Map<FboStocks, FboStocks>());
    setContext("selectedStocks", selectedStocks);

    let selectedStorage = writable(new Map<number, FboStorage>());
    setContext("selectedStorage", selectedStorage);

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

    onMount(async () => {
        const detail = fboWarehouseGrid()
            .plugin(
                new ChangesPlugin("id", innerChanges, ({ data }) => {
                    let stock = stocks.find(x => x.stocks.some(s => s.id === data.id));
                    console.log(stock);
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

        definition = fboOffersGrid()
            .plugin(new StatePlugin("fbo_storage"))
            .plugin(new ChangesPlugin("id", changes))
            .plugin(new ReadonlyPlugin(!$userCanModify))
            .plugin(new ZoomPlugin(href => (selected_image = href)))
            .plugin(new ClassesPlugin())
            .plugin(new RowSelectionPlugin(selectedStocks))
            .plugin(new DetailGridPlugin(detail, data => data.stocks));

        stocks = await fetchFboStocks();
    });

    let filter: Filter<FboStocks>;
</script>

{#if selected_image}
    <ImageWindow bind:src={selected_image} />
{/if}

<Toolbar bind:filter markets={data.options} />
{#if definition}
    <Grid {definition} bind:data={stocks} bind:filter />
{/if}
<Footer bind:changes on:reload={refreshData} on:save={save} />
