<script lang="ts">
    import Grid from "$lib/grid/Grid.svelte";
    import { onMount } from "svelte";
    import Footer from "../Footer.svelte";
    import { patchOwnStorages, type OwnStorage } from "$lib/data/own_storage";
    import { get, writable } from "svelte/store";
    import ownStorageGrid from "./grid";
    import type { GridDefinition } from "$lib/datagrid";
    import ChangesPlugin from "$lib/datagrid/plugins/changes";
    import StatePlugin from "$lib/datagrid/plugins/state";
    import ReadonlyPlugin from "$lib/datagrid/plugins/readonly";
    import ZoomPlugin from "$lib/datagrid/plugins/zoom";
    import ImageWindow from "$lib/components/windows/ImageWindow.svelte";
    import { userCanModify } from "$lib/data/user";
    import ClassesPlugin from "$lib/datagrid/plugins/classes";
    import type { Filter } from "$lib/datagrid/filters";
    import Toolbar from "./Toolbar.svelte";
    import type { PageData } from "./$types";
    import FilterPlugin from "$lib/datagrid/plugins/filter";
    import { ownStorageState } from "../state";

    export let data: PageData;

    let definition: GridDefinition;

    let selected_image: string | undefined = undefined;

    onMount(async () => {
        await ownStorageState.load();
        definition = ownStorageGrid(data.markets, data.storages)
            .plugin(new FilterPlugin(filterStore))
            .plugin(new StatePlugin("own_storage"))
            .plugin(new ChangesPlugin(x => x.offer.sku, ownStorageState.changes))
            .plugin(new ReadonlyPlugin(!$userCanModify))
            .plugin(new ZoomPlugin(href => (selected_image = href)))
            .plugin(new ClassesPlugin());
    });

    async function save() {
        let ok = await patchOwnStorages(
            get(ownStorageState).filter(x => get(ownStorageState.changes).isChanged(x.offer.sku))
        );
        if (ok) await ownStorageState.forceReload();
    }

    let filter: Filter<OwnStorage>;
    let filterStore = writable<Filter<OwnStorage>>();
    $: $filterStore = filter;
</script>

{#if selected_image}
    <ImageWindow bind:src={selected_image} />
{/if}

<Toolbar bind:filter markets={data.markets} />
{#if definition && $ownStorageState}
    <Grid {definition} bind:data={$ownStorageState} />
{/if}
<Footer
    changes={ownStorageState.changes}
    on:save={save}
    on:reload={() => ownStorageState.forceReload()}
    on:cancel={() => ownStorageState.cancel()}
/>
