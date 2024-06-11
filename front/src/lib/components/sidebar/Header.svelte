<script lang="ts">
    import { getContext } from "svelte";
    import type { Writable } from "svelte/store";
    import { fade } from "svelte/transition";

    export let text = "mp-auto-price";
    let collapsed = getContext<Writable<boolean>>("collapsed");
</script>

<header>
    <button class:collapsed={$collapsed} on:click={() => ($collapsed = !$collapsed)}>
        <img src="/list.svg" alt="" />
    </button>
    {#if !$collapsed}
        <h1 out:fade={{ delay: 500, duration: 0 }}>{text}</h1>
    {/if}
</header>

<style lang="scss">
    @use "mixins" as *;

    header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-direction: row-reverse;
        align-self: stretch;
        height: 48px;
        > h1 {
            flex: 1 0 0;
            font-size: 16px;
            margin-left: 12px;
            text-overflow: clip;
            white-space: nowrap;
        }
        > button {
            width: 48px;
            cursor: pointer;
        }
    }

    button {
        display: flex;
        justify-content: center;
        align-items: center;
        color: white;
        background-color: transparent;
        border: 0;
        flex: 0 0 48px;
        height: 48px;

        &:hover {
            background-color: #4f6372;
        }

        > img {
            width: 24px;
            height: 24px;
            filter: invert(1);
        }
    }
</style>
