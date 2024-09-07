<script lang="ts">
    import { logout } from "$lib/auth";
    import Header from "$lib/components/sidebar/Header.svelte";
    import Link from "$lib/components/sidebar/Link.svelte";
    import Spacer from "$lib/components/sidebar/Spacer.svelte";
    import { user } from "$lib/data/user";
    import { setContext } from "svelte";
    import { writable } from "svelte/store";
    import type { LayoutData } from "./$types";

    export let data: LayoutData;
    $: $user = data.user;

    let collapsed = writable(true);
    setContext("collapsed", collapsed);
</script>

<div id="wrapper" class:collapsed={$collapsed}>
    <nav>
        <Header name={$user?.login} />
        <Link text="Карточки" icon="/barcode.svg" path="/app/offers" />
        <Link text="Каталог" icon="/tag.svg" path="/app/catalog" />
        <Link text="Мои остатки" icon="/warehouse.svg" path="/app/own_storage" />
        <Link text="FBO остатки" icon="/package.svg" path="/app/fbo_storage" />
        <Spacer />
        <Link text="Шаблоны цен" icon="/math.svg" path="/app/templates" />
        <Link text="Магазины" icon="/storefront.svg" path="/app/markets" />
        <Link text="Выход" icon="/sign-out.svg" path="/auth" on:click={logout} />
    </nav>
    <slot />
</div>

<style lang="scss">
    #wrapper {
        display: grid;
        grid-template-rows: minmax(0, 1fr);
        grid-template-columns: var(--sidebar-width) 1fr;
        grid-template-areas: "sidebar content";

        width: 100%;
        height: 100%;

        transition: grid-template-columns 0.5s;
        --sidebar-width: 200px;
        &.collapsed {
            --sidebar-width: 48px;
        }
    }
    nav {
        grid-area: sidebar;

        display: flex;
        align-items: stretch;
        flex-direction: column;

        color: white;
        background-color: #455561;
        overflow: hidden;
    }
</style>
