<script lang="ts">
    import type { LayoutData } from "./$types";
    import Menu from "./Menu.svelte";
    import { browser } from "$app/environment";
    import { filterState } from "./state";

    export let data: LayoutData;

    if (browser) {
        filterState.init(data.markets);
    }
</script>

<main>
    <Menu />
    <slot />
</main>

<style lang="scss">
    @use "mixins" as *;

    main {
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }
</style>
