<script lang="ts">
    import { writable } from "svelte/store";
    import Menu from "./Menu.svelte";
    import { setContext } from "svelte";

    let refresh = writable(() => {});
    setContext("refresh", refresh); // FIXME: better solution is needed
</script>

<main>
    <Menu on:import={$refresh} />
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
