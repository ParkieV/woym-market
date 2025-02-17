<script lang="ts">
    import Grid from "$lib/grid/Grid.svelte";
    import { onMount } from "svelte";
    import Footer from "../Footer.svelte";
    import { get } from "svelte/store";
    import type { GridDefinition } from "$lib/datagrid";
    import catalogGrid from "./grid";
    import StatePlugin from "$lib/datagrid/plugins/state";
    import ChangesPlugin from "$lib/datagrid/plugins/changes";
    import { userCanModify } from "$lib/data/user";
    import ReadonlyPlugin from "$lib/datagrid/plugins/readonly";
    import ZoomPlugin from "$lib/datagrid/plugins/zoom";
    import ImageWindow from "$lib/components/windows/ImageWindow.svelte";
    import ClassesPlugin from "$lib/datagrid/plugins/classes";
    import Toolbar from "./Toolbar.svelte";
    import FilterPlugin from "$lib/datagrid/plugins/filter";
    import { catalogState, invalidateAllState } from "../state";
    import { updateCatalog, type CatalogEntry } from "$lib/data/catalog";
    import catalogFilter from "./filter";
    import type { PageData } from "./$types";

    export let data: PageData;

    onMount(() => catalogState.load());

    let definition: GridDefinition<CatalogEntry>;

    async function save() {
        let ok = await updateCatalog(
            get(catalogState).filter(x => get(catalogState.changes).isChanged(x.sku))
        );
        if (ok) {
            await invalidateAllState();
            await catalogState.forceReload();
        }
    }

    onMount(async () => {
        definition = catalogGrid(data.markets)
            .plugin(new FilterPlugin(catalogFilter))
            .plugin(new StatePlugin("offers"))
            .plugin(new ChangesPlugin(x => x.sku, catalogState.changes))
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
                        } else if (colDef.field === "name") {
                            return data.name?.length > 60;
                        }
                        return false;
                    }
                })
            );
    });

    let selected_image: string | undefined = undefined;
</script>

{#if selected_image}
    <ImageWindow bind:src={selected_image} />
{/if}

<Toolbar />
{#if definition}
    <Grid {definition} bind:data={$catalogState} />
{/if}
<Footer
    changes={catalogState.changes}
    on:save={save}
    on:reload={() => catalogState.forceReload()}
    on:cancel={() => catalogState.cancel()}
/>
