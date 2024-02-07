<script lang="ts">
    import Menu from "./Menu.svelte";
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
        flex: 1;
    }
</style>
