<script lang="ts">
    import Grid from "$lib/components/datagrid/Grid.svelte";
    import { onMount } from "svelte";
    import { type Offer, fetchOfferList, patchOfferList } from "$lib/data/offers";
    import { ChangeList } from "$lib/components/datagrid/changes";
    import Toolbar from "./Toolbar.svelte";
    import type { Column, ColumnGroup } from "$lib/components/datagrid/columns";
    import Footer from "./Footer.svelte";
    import { fetchTemplates, type Template } from "$lib/data/templates";
    import { offerColumns } from "$lib/columns";

    let data: Offer[] = [];
    let changes = new ChangeList<Offer, "sku">();
    let columns: (Column | ColumnGroup)[] = [];

    /** Refreshes data displayed in the grid. */
    async function refreshData() {
        changes.clear();
        changes = changes;
        data = await fetchOfferList();
    }

    async function save() {
        let ok = await patchOfferList(data.filter(x => changes.isChanged(x.sku)));
        if (ok) await refreshData();
    }

    onMount(async () => {
        let templates: Template[] = await fetchTemplates();
        columns = offerColumns(templates);
        refreshData();
    });

    let filter: (offer: Offer) => boolean = () => true;
</script>

<main>
    <Toolbar
        on:filterChanged={e => {
            filter = e.detail;
        }}
    />
    {#if columns.length !== 0}
        <Grid grid_name="offers" key="sku" {columns} bind:data bind:changes bind:filter />
    {/if}
    <Footer bind:changes on:reload={refreshData} on:save={save} />
</main>

<style lang="scss">
    main {
        display: flex;
        flex-direction: column;
        flex: 1;
    }
</style>
