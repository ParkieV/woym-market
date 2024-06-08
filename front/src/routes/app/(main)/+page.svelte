<script lang="ts">
    import Grid from "$lib/grid/Grid.svelte";
    import { getContext, onMount } from "svelte";
    import { type Offer, fetchOfferList, patchOfferList } from "$lib/data/offers";
    import Footer from "./Footer.svelte";
    import { fetchTemplates, type Template } from "$lib/data/templates";
    import type { Writable } from "svelte/store";
    import { type FilterParams, offerBaseFilter } from "$lib/grid/filters";
    import type { GridDefinition } from "$lib/components/datagrid";
    import offerGrid from "./grid";
    import StatePlugin from "$lib/components/datagrid/plugins/state";
    import ChangesPlugin, { ChangeList } from "$lib/components/datagrid/plugins/changes";
    import { userCanModify } from "$lib/data/user";
    import ReadonlyPlugin from "$lib/components/datagrid/plugins/readonly";
    import ZoomPlugin from "$lib/components/datagrid/plugins/zoom";
    import ImageWindow from "$lib/components/windows/ImageWindow.svelte";
    import ClassesPlugin from "$lib/components/datagrid/plugins/classes";

    let definition: GridDefinition<Offer>;
    let data: Offer[] = [];
    let changes = new ChangeList<Offer, "id">();

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

        definition = offerGrid(templates)
            .plugin(StatePlugin("offers"))
            .plugin(ChangesPlugin("id", changes))
            .plugin(ReadonlyPlugin(!$userCanModify))
            .plugin(ZoomPlugin(href => (selected_image = href)))
            .plugin(ClassesPlugin());

        refreshData();
    });

    let filterParams = getContext<Writable<FilterParams>>("filterParams");
    $: filter = offerBaseFilter($filterParams);

    let selected_image: string | undefined = undefined;
</script>

{#if selected_image}
    <ImageWindow bind:src={selected_image} />
{/if}
{#if definition}
    <Grid {definition} bind:data bind:filter />
{/if}
<Footer bind:changes on:reload={refreshData} on:save={save} />
