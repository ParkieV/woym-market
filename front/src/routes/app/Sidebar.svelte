<script lang="ts">
    import { createEventDispatcher } from "svelte";
    import { fade, slide } from "svelte/transition";

    let dispatch = createEventDispatcher<{
        settings: void;
        exit: void;
    }>();

    let collapsed = false;

    type Entry = "spacer" | { name: string; icon: string; onclick: () => void };
    const entries: Entry[] = [
        "spacer",
        { name: "Настройки", icon: "gear.svg", onclick: () => dispatch("settings") },
        { name: "Выход", icon: "sign-out.svg", onclick: () => dispatch("exit") }
    ];
</script>

<nav class:collapsed>
    <header>
        <button on:click={() => (collapsed = !collapsed)}>
            <img src="list.svg" alt="" />
        </button>
        {#if !collapsed}
            <h1 out:fade={{ delay: 500, duration: 0 }}>mp-auto-price</h1>
        {/if}
    </header>
    {#each entries as entry}
        {#if entry == "spacer"}
            <div style="flex: 1;" />
        {:else}
            {@const { name, icon, onclick } = entry}
            <button class="sign-out" on:click={onclick}>
                <img src={icon} alt="" />
                {#if !collapsed}
                    <span transition:slide={{ duration: 500, axis: "x" }}>
                        {name}
                    </span>
                {/if}
            </button>
        {/if}
    {/each}
</nav>

<style lang="scss">
    nav {
        --sidebar-width: 200px;

        flex: 0 0 min(100vw, var(--sidebar-width));
        transition: flex 0.5s;

        display: flex;
        align-items: center;
        flex-direction: column;

        color: white;
        background-color: #455561;
        overflow: hidden;

        button {
            height: 48px;
            padding: 12px;
            > img {
                width: 24px;
                height: 24px;
            }
        }

        > header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-direction: row-reverse;
            align-self: stretch;
            > h1 {
                flex: 1;
                font-size: 16px;
                margin-left: 12px;
            }
        }

        &:not(.collapsed) {
            > button {
                padding: 20px 20px;
                gap: 8px;
            }
        }

        &.collapsed {
            --sidebar-width: 48px;
            // flex: 0 0 48px;
        }
    }

    button {
        display: flex;
        justify-content: center;
        align-items: center;
        align-self: stretch;
        color: white;
        background-color: transparent;
        border: none;
        > img {
            width: 21px;
            height: 21px;
            filter: invert(1);
        }
        &:hover {
            background-color: rgba(0, 0, 0, 0.2);
        }
    }

    span,
    h1 {
        text-overflow: clip;
        white-space: nowrap;
    }
</style>
