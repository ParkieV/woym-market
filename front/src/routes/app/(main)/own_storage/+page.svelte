<script lang="ts">
    import Grid from "$lib/grid/Grid.svelte";
    import { getContext, onMount } from "svelte";
    import Footer from "../Footer.svelte";
    import { fetchOwnStorages, patchOwnStorages, type OwnStorage } from "$lib/data/own_storage";
    import type { Writable } from "svelte/store";
    import { ownStorageFilter, type FilterParams } from "$lib/grid/filters";
    import ownStorageGrid from "./grid";
    import type { GridDefinition } from "$lib/components/datagrid";
    import ChangesPlugin, { ChangeList } from "$lib/components/datagrid/plugins/changes";
    import StatePlugin from "$lib/components/datagrid/plugins/state";
    import ReadonlyPlugin from "$lib/components/datagrid/plugins/readonly";
    import ZoomPlugin from "$lib/components/datagrid/plugins/zoom";
    import ImageWindow from "$lib/components/windows/ImageWindow.svelte";
    import { userCanModify } from "$lib/data/user";
    import ClassesPlugin from "$lib/components/datagrid/plugins/classes";

    let definition: GridDefinition;
    let data: OwnStorage[] = [];
    let changes = new ChangeList<OwnStorage, "sku">();

    let refresh = getContext<Writable<() => {}>>("refresh");
    $refresh = refreshData;

    let filterParams = getContext<Writable<FilterParams>>("filterParams");
    $: filter = ownStorageFilter($filterParams);

    let selected_image: string | undefined = undefined;

    onMount(async () => {
        let info = await fetchOwnStorages();
        data = info.data;

        definition = ownStorageGrid(info.markets)
            .plugin(StatePlugin("own_storage"))
            .plugin(ChangesPlugin("sku", changes))
            .plugin(ReadonlyPlugin(!$userCanModify))
            .plugin(ZoomPlugin(href => (selected_image = href)))
            .plugin(ClassesPlugin());
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

{#if selected_image}
    <ImageWindow bind:src={selected_image} />
{/if}
{#if definition}
    <Grid {definition} bind:data bind:filter />
{/if}
<Footer bind:changes on:reload={refreshData} on:save={save} />
