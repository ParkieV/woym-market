<script lang="ts">
    import Grid from "$lib/grid/Grid.svelte";
    import { getContext, onMount } from "svelte";
    import Footer from "../Footer.svelte";
    import { fetchOwnStorages, patchOwnStorages, type OwnStorage } from "$lib/data/own_storage";
    import type { Writable } from "svelte/store";
    import ownStorageGrid from "./grid";
    import type { GridDefinition } from "$lib/datagrid";
    import ChangesPlugin, { ChangeList } from "$lib/datagrid/plugins/changes";
    import StatePlugin from "$lib/datagrid/plugins/state";
    import ReadonlyPlugin from "$lib/datagrid/plugins/readonly";
    import ZoomPlugin from "$lib/datagrid/plugins/zoom";
    import ImageWindow from "$lib/components/windows/ImageWindow.svelte";
    import { userCanModify } from "$lib/data/user";
    import ClassesPlugin from "$lib/datagrid/plugins/classes";
    import type { Filter } from "$lib/datagrid/filters";
    import Toolbar from "./Toolbar.svelte";
    import type { PageData } from "./$types";

    export let data: PageData;

    let definition: GridDefinition;
    let storage: OwnStorage[] = [];
    let changes = new ChangeList<OwnStorage, "sku">();

    let refresh = getContext<Writable<() => {}>>("refresh");
    $refresh = refreshData;

    let selected_image: string | undefined = undefined;

    onMount(async () => {
        let info = await fetchOwnStorages();
        storage = info.data;

        definition = ownStorageGrid(info.markets)
            .plugin(new StatePlugin("own_storage"))
            .plugin(new ChangesPlugin("sku", changes))
            .plugin(new ReadonlyPlugin(!$userCanModify))
            .plugin(new ZoomPlugin(href => (selected_image = href)))
            .plugin(new ClassesPlugin());
    });

    async function save() {
        let ok = await patchOwnStorages(storage.filter(x => changes.isChanged(x.sku)));
        if (ok) await refreshData();
    }

    async function refreshData() {
        changes.clear();
        changes = changes;
        storage = (await fetchOwnStorages()).data;
    }

    let filter: Filter<OwnStorage>;
</script>

{#if selected_image}
    <ImageWindow bind:src={selected_image} />
{/if}

<Toolbar bind:filter markets={data.options} />
{#if definition}
    <Grid {definition} bind:data={storage} bind:filter />
{/if}
<Footer bind:changes on:reload={refreshData} on:save={save} />
