<script lang="ts">
    import Grid from "$lib/grid/Grid.svelte";
    import { getContext, onMount } from "svelte";
    import { type Offer, fetchOfferList, patchOfferList } from "$lib/data/offers";
    import Footer from "./Footer.svelte";
    import { fetchTemplates, type Template } from "$lib/data/templates";
    import type { Writable } from "svelte/store";
    import type { GridDefinition } from "$lib/components/datagrid";
    import offerGrid from "./grid";
    import StatePlugin from "$lib/components/datagrid/plugins/state";
    import ChangesPlugin, { ChangeList } from "$lib/components/datagrid/plugins/changes";
    import { userCanModify } from "$lib/data/user";
    import ReadonlyPlugin from "$lib/components/datagrid/plugins/readonly";
    import ZoomPlugin from "$lib/components/datagrid/plugins/zoom";
    import ImageWindow from "$lib/components/windows/ImageWindow.svelte";
    import ClassesPlugin from "$lib/components/datagrid/plugins/classes";
    import Toolbar from "./Toolbar.svelte";
    import type { PageData } from "./$types";
    import type { Filter } from "$lib/components/datagrid/filters";

    export let data: PageData;

    let definition: GridDefinition<Offer>;
    let offers: Offer[] = [];
    let changes = new ChangeList<Offer, "id">();

    /** Refreshes data displayed in the grid. */
    async function refreshData() {
        changes.clear();
        changes = changes;
        offers = await fetchOfferList();
    }

    async function save() {
        let ok = await patchOfferList(offers.filter(x => changes.isChanged(x.id)));
        if (ok) await refreshData();
    }

    let refresh = getContext<Writable<() => {}>>("refresh");
    $refresh = refreshData;

    onMount(async () => {
        let templates: Template[] = await fetchTemplates();

        definition = offerGrid(templates)
            .plugin(new StatePlugin("offers"))
            .plugin(new ChangesPlugin("id", changes))
            .plugin(new ReadonlyPlugin(!$userCanModify))
            .plugin(new ZoomPlugin(href => (selected_image = href)))
            .plugin(
                new ClassesPlugin({
                    warning: ({ colDef, data }) => {
                        if (colDef.field !== "current_price") return false;
                        return data.current_price !== data.target_price;
                    },
                    error: ({ colDef, data }) => {
                        if (colDef.field === "your_promotion_price") {
                            return data.stop_price > data.your_promotion_price;
                        } else if (colDef.field === "target_price") {
                            return data.stop_price > data.target_price;
                        } else if (colDef.field === "current_price") {
                            return data.stop_price > data.current_price;
                        }
                        return false;
                    }
                })
            );

        refreshData();
    });

    let filter: Filter<Offer>;
    let selected_image: string | undefined = undefined;
</script>

{#if selected_image}
    <ImageWindow bind:src={selected_image} />
{/if}

<Toolbar bind:filter markets={data.options} />
{#if definition}
    <Grid {definition} bind:data={offers} bind:filter />
{/if}
<Footer bind:changes on:reload={refreshData} on:save={save} />
