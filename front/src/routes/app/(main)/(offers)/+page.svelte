<script lang="ts">
    import Grid from "$lib/grid/Grid.svelte";
    import { onMount } from "svelte";
    import { type Offer, patchOfferList } from "$lib/data/offers";
    import Footer from "../Footer.svelte";
    import { fetchTemplates, type Template } from "$lib/data/templates";
    import { writable, get } from "svelte/store";
    import type { GridDefinition } from "$lib/datagrid";
    import offerGrid from "./grid";
    import StatePlugin from "$lib/datagrid/plugins/state";
    import ChangesPlugin from "$lib/datagrid/plugins/changes";
    import { userCanModify } from "$lib/data/user";
    import ReadonlyPlugin from "$lib/datagrid/plugins/readonly";
    import ZoomPlugin from "$lib/datagrid/plugins/zoom";
    import ImageWindow from "$lib/components/windows/ImageWindow.svelte";
    import ClassesPlugin from "$lib/datagrid/plugins/classes";
    import Toolbar from "./Toolbar.svelte";
    import type { PageData } from "./$types";
    import type { Filter } from "$lib/datagrid/filters";
    import FilterPlugin from "$lib/datagrid/plugins/filter";
    import { offersState } from "../state";

    onMount(() => offersState.load());

    export let data: PageData;

    let definition: GridDefinition<Offer>;

    async function save() {
        let ok = await patchOfferList(
            get(offersState).filter(x => get(offersState.changes).isChanged(x.id))
        );
        if (ok) await offersState.forceReload();
    }

    onMount(async () => {
        let templates: Template[] = await fetchTemplates();

        definition = offerGrid(templates)
            .plugin(new FilterPlugin(filterStore))
            .plugin(new StatePlugin("offers"))
            .plugin(new ChangesPlugin(x => x.id, offersState.changes))
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
    });

    let filter: Filter<Offer>;
    let filterStore = writable<Filter<Offer>>();
    $: $filterStore = filter;

    let selected_image: string | undefined = undefined;
</script>

{#if selected_image}
    <ImageWindow bind:src={selected_image} />
{/if}

<Toolbar bind:filter markets={data.markets} />
{#if definition}
    <Grid {definition} bind:data={$offersState} />
{/if}
<Footer
    changes={offersState.changes}
    on:save={save}
    on:reload={() => offersState.forceReload()}
    on:cancel={() => offersState.cancel()}
/>
