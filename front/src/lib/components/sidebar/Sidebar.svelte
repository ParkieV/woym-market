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
    <Link text="Остатки" icon="/package.svg" path="/app/storage" />
    <Link text="Яндекс" icon="/yandex.svg" path="/app/storage/yandex" />
    <Spacer />
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
