<script lang="ts">
    import Grid from "$lib/components/datagrid/Grid.svelte";
    import { ChangeList } from "$lib/components/datagrid/changes";
    import type { Column, ColumnGroup } from "$lib/components/datagrid/columns";
    import { getContext, onMount } from "svelte";
    import Footer from "../Footer.svelte";
    import { ownStorageColumns } from "$lib/grid/columns";
    import { fetchOwnStorages, patchOwnStorages, type OwnStorage } from "$lib/data/own_storage";
    import type { Writable } from "svelte/store";
    import { ownStorageFilter, type FilterParams } from "$lib/grid/filters";

    let data: OwnStorage[] = [];
    let changes = new ChangeList<OwnStorage, "sku">();
    let columns: (Column | ColumnGroup)[] = [];

    let refresh = getContext<Writable<() => {}>>("refresh");
    $refresh = refreshData;

    let filterParams = getContext<Writable<FilterParams>>("filterParams");
    $: filter = ownStorageFilter($filterParams);

    onMount(async () => {
        let info = await fetchOwnStorages();
        columns = ownStorageColumns(info.markets);
        data = info.data;
    });

    async function save() {
        let ok = await patchOwnStorages(data.filter(x => changes.isChanged(x.sku)));
        if (ok) await refreshData();
    }

    async function refreshData() {
        changes.clear();
        changes = changes;
        data = (await fetchOwnStorages()).data;
    }
</script>

{#if columns.length !== 0}
    <Grid grid_name="own_storage" key="sku" {columns} bind:data bind:changes {filter} />
{/if}
<Footer bind:changes on:reload={refreshData} on:save={save} />
