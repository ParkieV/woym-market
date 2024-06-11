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
    import type { Writable } from "svelte/store";
    import ChangesPlugin, { ChangeList } from "$lib/components/datagrid/plugins/changes";
    import type { GridDefinition } from "$lib/components/datagrid";
    import ImageWindow from "$lib/components/windows/ImageWindow.svelte";
    import fboOffersGrid from "./fbo-offer";
    import StatePlugin from "$lib/components/datagrid/plugins/state";
    import ReadonlyPlugin from "$lib/components/datagrid/plugins/readonly";
    import ZoomPlugin from "$lib/components/datagrid/plugins/zoom";
    import { userCanModify } from "$lib/data/user";
    import ClassesPlugin from "$lib/components/datagrid/plugins/classes";
    import type { Filter } from "$lib/components/datagrid/filters";
    import Toolbar from "./Toolbar.svelte";
    import type { PageData } from "./$types";

    export let data: PageData;

    let definition: GridDefinition;
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

    onMount(async () => {
        definition = (
            await fboOffersGrid(innerChanges, id => {
                changes.add(id);
                changes = changes;
            })
        )
            .plugin(StatePlugin("fbo_storage"))
            .plugin(ChangesPlugin("id", changes))
            .plugin(ReadonlyPlugin(!$userCanModify))
            .plugin(ZoomPlugin(href => (selected_image = href)))
            .plugin(ClassesPlugin());

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
