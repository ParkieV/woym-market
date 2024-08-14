<script lang="ts">
    import { getContext } from "svelte";
    import type { Writable } from "svelte/store";
    import { slide } from "svelte/transition";
    import { page } from "$app/stores";

    export let text: string;
    export let icon: string;
    export let path: string | undefined = undefined;

    let collapsed = getContext<Writable<boolean>>("collapsed");
</script>

{#if path === undefined}
    <button
        on:click
        title={$collapsed ? text : undefined}
        class:collapsed={$collapsed}
        class:current={path ? $page.url.pathname.startsWith(path) : false}
    >
        <img src={icon} alt="" />
        {#if !$collapsed}
            <span transition:slide={{ duration: 500, axis: "x" }}>
                {text}
            </span>
        {/if}
    </button>
{:else}
    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <a
        on:click
        href={path}
        title={$collapsed ? text : undefined}
        class:collapsed={$collapsed}
        class:current={path ? $page.url.pathname.startsWith(path) : false}
    >
        <img src={icon} alt="" />
        {#if !$collapsed}
            <span transition:slide={{ duration: 500, axis: "x" }}>
                {text}
            </span>
        {/if}
    </a>
{/if}

<style lang="scss">
    @use "mixins" as *;

    a,
    button {
        display: flex;
        justify-content: start;
        align-items: center;
        color: white;
        background-color: transparent;
        border: 0;
        height: 48px;
        text-decoration: none;
        cursor: pointer;
        font-size: 16px;

        &:hover {
            background-color: #4f6372;
        }
        &.current {
            background-color: #647c8f;
        }

        transition:
            padding 0.5s,
            gap 0.5s;

        &.collapsed {
            padding: 0 12px;
            gap: 0px;
        }

        &:not(.collapsed) {
            padding: 0 20px;
            gap: 12px;
        }

        > img {
            width: 24px;
            height: 24px;
            filter: invert(1);
        }
    }

    span {
        text-overflow: clip;
        white-space: nowrap;
    }
</style>
