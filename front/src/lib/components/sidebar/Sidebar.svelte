<script lang="ts">
    import { logout } from "$lib/auth";
    import Link from "./Link.svelte";
    import Spacer from "./Spacer.svelte";
    import { setContext } from "svelte";
    import Header from "./Header.svelte";
    import { writable } from "svelte/store";

    let collapsed = writable(true);
    setContext("collapsed", collapsed);
</script>

<nav class:collapsed={$collapsed}>
    <Header />
    <Link text="Товары" icon="/house.svg" path="/app" />
    <Link text="Мои остатки" icon="/warehouse.svg" path="/app/own_storage" />
    <Link text="FBO остатки" icon="/package.svg" path="/app/fbo_storage" />
    <Spacer />
    <Link text="Шаблоны цен" icon="/math.svg" path="/app/templates" />
    <Link text="Настройки" icon="/gear.svg" path="/app/settings" />
    <Link text="Выход" icon="/sign-out.svg" path="/auth" on:click={logout} />
</nav>

<style lang="scss">
    nav {
        flex: 0 0 min(100vw, var(--sidebar-width));
        transition: flex 0.5s;

        display: flex;
        align-items: stretch;
        flex-direction: column;

        color: white;
        background-color: #455561;
        overflow: hidden;

        &.collapsed {
            --sidebar-width: 48px;
        }
        &:not(.collapsed) {
            --sidebar-width: 200px;
        }
    }
</style>
