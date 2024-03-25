<script lang="ts">
    import { logout } from "$lib/auth";
    import Header from "$lib/components/sidebar/Header.svelte";
    import Link from "$lib/components/sidebar/Link.svelte";
    import Spacer from "$lib/components/sidebar/Spacer.svelte";
    import { user } from "$lib/data/user";
    import { setContext } from "svelte";
    import { writable } from "svelte/store";
    import { page } from "$app/stores";
    import { BaseUrl } from "$lib";
    import type { LayoutData } from "./$types";

    export let data: LayoutData;
    $: $user = data.user;

    let collapsed = writable(true);
    setContext("collapsed", collapsed);

    let name = "mp-auto-price";
    $: name = $user?.login ?? "mp-auto-price";

    $: is_dev_frontend = $page.url.hostname === "localhost" || $page.url.hostname.startsWith("dev");
    $: is_dev_backend = BaseUrl.includes("dev.oy-pro.ru");
    $: show_warning = is_dev_frontend && !is_dev_backend;
</script>

<div id="wrapper" class:collapsed={$collapsed} class:warning={show_warning}>
    <nav>
        <Header text={name} />
        <Link text="Товары" icon="/house.svg" path="/app" />
        <Link text="Мои остатки" icon="/warehouse.svg" path="/app/own_storage" />
        <Link text="FBO остатки" icon="/package.svg" path="/app/fbo_storage" />
        <Spacer />
        <Link text="Шаблоны цен" icon="/math.svg" path="/app/templates" />
        <Link text="Настройки" icon="/gear.svg" path="/app/settings" />
        <Link text="Выход" icon="/sign-out.svg" path="/auth" on:click={logout} />
    </nav>
    {#if show_warning}
        <div class="dev-warning">
            localhost или dev-сервер запущен с путём API production-сервера!
        </div>
    {/if}
    <slot />
</div>

<style lang="scss">
    #wrapper {
        display: grid;
        grid-template-rows: minmax(0, 1fr);
        grid-template-columns: var(--sidebar-width) 1fr;
        grid-template-areas: "sidebar content";

        &.warning {
            grid-template-rows: 40px minmax(0, 1fr);
            grid-template-areas:
                "sidebar warning"
                "sidebar content";
        }

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
    .dev-warning {
        grid-area: warning;

        display: flex;
        align-items: center;
        justify-content: center;

        height: 40px;

        font-size: 20px;
        font-weight: bold;
        color: white;
        background-color: rgb(172, 0, 0);
    }
</style>
