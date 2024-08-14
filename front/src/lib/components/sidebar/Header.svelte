<script lang="ts">
    import { userCanModify } from "$lib/data/user";
    import { getContext } from "svelte";
    import type { Writable } from "svelte/store";
    import { fade } from "svelte/transition";

    export let name = "Unknown";
    let collapsed = getContext<Writable<boolean>>("collapsed");
</script>

<header>
    <button class:collapsed={$collapsed} on:click={() => ($collapsed = !$collapsed)}>
        <img src="/list.svg" alt="" />
    </button>
    {#if !$collapsed}
        {@const canEdit = $userCanModify ? "" : " (Доступ только для чтения)"}
        {@const lock = $userCanModify ? "" : " 🔒"}
        <h1 title={`Пользователь ${name}${canEdit}`} out:fade={{ delay: 500, duration: 0 }}>
            <img src="/user.svg" alt="" />
            <span>{`${name}${lock}`}</span>
        </h1>
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
        border-bottom: 1px solid hsl(206, 17%, 50%);
        margin-bottom: 20px;
        box-sizing: content-box;

        > h1 {
            display: flex;
            align-items: center;
            gap: 12px;

            flex: 1 0 0;
            font-size: 16px;
            margin-left: 20px;
            text-overflow: clip;
            white-space: nowrap;

            font-weight: normal;
            font-size: 18px;

            > img {
                width: 24px;
                height: 24px;
                filter: invert(1);
            }
        }
        > button {
            @include button;
            background-color: transparent;
            border: 0;
            border-radius: 0;
            flex: 0 0 48px;
            width: 48px;
            height: 48px;

            &:hover {
                background-color: #4f6372;
            }

            > img {
                width: 24px;
                height: 24px;
                filter: invert(1);
            }
            cursor: pointer;
        }
    }
</style>
