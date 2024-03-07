<script lang="ts">
    import { logout } from "$lib/auth";
    import Header from "$lib/components/sidebar/Header.svelte";
    import Link from "$lib/components/sidebar/Link.svelte";
    import Spacer from "$lib/components/sidebar/Spacer.svelte";
    import { user } from "$lib/user";
    import { onMount, setContext } from "svelte";
    import { writable } from "svelte/store";
    import { fetchUser } from "$lib/user";

    let collapsed = writable(true);
    setContext("collapsed", collapsed);

    let name = "mp-auto-price";
    $: name = $user?.login ?? "mp-auto-price";

    onMount(() => {
        $user = undefined;
        fetchUser();
    });
</script>

<div id="wrapper">
    <nav class:collapsed={$collapsed}>
        <Header text={name} />
        <Link text="Товары" icon="/house.svg" path="/app" />
        <Link text="Мои остатки" icon="/warehouse.svg" path="/app/own_storage" />
        <Link text="FBO остатки" icon="/package.svg" path="/app/fbo_storage" />
        <Spacer />
        <Link text="Шаблоны цен" icon="/math.svg" path="/app/templates" />
        <Link text="Настройки" icon="/gear.svg" path="/app/settings" />
        <Link text="Выход" icon="/sign-out.svg" path="/auth" on:click={logout} />
    </nav>
    <slot />
</div>

<style lang="scss">
    #wrapper {
        display: flex;
        align-items: stretch;
        height: 100%;
    }
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
