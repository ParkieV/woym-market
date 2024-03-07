<script lang="ts">
    import { writable, type Writable } from "svelte/store";
    import Menu from "./Menu.svelte";
    import { setContext } from "svelte";
    import Toolbar from "./Toolbar.svelte";
    import type { FilterParams } from "$lib/grid/filters";

    let refresh = writable(() => {});
    setContext("refresh", refresh); // FIXME: better solution is needed

    let filterParams = writable<FilterParams>({
        markets: [],
        shops: [],
        search: "",
        show_hidden: false
    });
    setContext<Writable<FilterParams>>("filterParams", filterParams);
</script>

<main>
    <Menu on:import={$refresh} />
    <Toolbar on:filterChanged={e => ($filterParams = e.detail)} />
    <slot />
</main>

<style lang="scss">
    @use "mixins" as *;

    main {
        display: flex;
        flex-direction: column;
        flex: 1;
    }
</style>
