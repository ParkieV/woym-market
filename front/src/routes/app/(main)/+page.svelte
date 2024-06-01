<script lang="ts">
    import Grid from "$lib/components/datagrid/Grid.svelte";
    import { getContext, onMount } from "svelte";
    import { type Offer, fetchOfferList, patchOfferList } from "$lib/data/offers";
    import { ChangeList } from "$lib/components/datagrid/changes";
    import type { Column, ColumnGroup } from "$lib/components/datagrid/columns";
    import Footer from "./Footer.svelte";
    import { fetchTemplates, type Template } from "$lib/data/templates";
    import offerColumns from "$lib/grid/columns/offer";
    import type { Writable } from "svelte/store";
    import { type FilterParams, offerBaseFilter } from "$lib/grid/filters";

    let data: Offer[] = [];
    let changes = new ChangeList<Offer, "id">();
    let columns: (Column | ColumnGroup)[] = [];

    /** Refreshes data displayed in the grid. */
    async function refreshData() {
        changes.clear();
        changes = changes;
        data = await fetchOfferList();
    }

    async function save() {
        let ok = await patchOfferList(data.filter(x => changes.isChanged(x.id)));
        if (ok) await refreshData();
    }

    let refresh = getContext<Writable<() => {}>>("refresh");
    $refresh = refreshData;

    onMount(async () => {
        let templates: Template[] = await fetchTemplates();
        columns = offerColumns(templates);
        refreshData();
    });

    let filterParams = getContext<Writable<FilterParams>>("filterParams");
    $: filter = offerBaseFilter($filterParams);
</script>

{#if columns.length !== 0}
    <Grid grid_name="offers" key="id" {columns} bind:data bind:changes bind:filter />
{/if}
<Footer bind:changes on:reload={refreshData} on:save={save} />
