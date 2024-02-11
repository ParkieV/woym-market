<script lang="ts">
    import Grid from "$lib/components/datagrid/Grid.svelte";
    import { ChangeList } from "$lib/components/datagrid/changes";
    import type { Column, ColumnGroup } from "$lib/components/datagrid/columns";
    import { onMount } from "svelte";
    import Footer from "../Footer.svelte";
    import columnList from "./column_list";
    import { fetchOwnStorages, type OwnStorage } from "$lib/data/own_storage";
    import { getStores as fetchStores } from "$lib/data/stores";
    import Toolbar from "../Toolbar.svelte";

    let data: OwnStorage[] = [];
    let changes = new ChangeList<OwnStorage, "sku">();
    let columns: (Column | ColumnGroup)[] = [];
    let filter: (storage: OwnStorage) => boolean = () => true;

    onMount(async () => {
        columns = columnList(await fetchStores());
        data = await fetchOwnStorages();
    });
</script>

<Toolbar on:filterChanged={f => (filter = f.detail)} />
{#if columns.length !== 0}
    <Grid grid_name="storage" key="sku" {columns} bind:data bind:changes {filter} />
{/if}
<Footer bind:changes />
