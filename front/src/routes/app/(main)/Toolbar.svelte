<script lang="ts">
    import ButtonGroup from "$lib/components/ButtonGroup.svelte";
    import Search from "$lib/components/Search.svelte";
    import { getStoreNames, getStoreTypes } from "$lib/data/markets";
    import type { FilterParams } from "$lib/grid/filters";
    import { createEventDispatcher, onMount } from "svelte";

    let shops: { key: string; name: string; selected: boolean }[] = [];
    let markets: { key: string; name: string; selected: boolean }[] = [];
    let search = "";
    let show_hidden: boolean = false;

    let dispatch = createEventDispatcher<{ filterChanged: FilterParams }>();
    $: {
        search, shops, markets, show_hidden;
        dispatch("filterChanged", { markets, shops, search, show_hidden });
    }

    onMount(async () => {
        [shops, markets] = (await Promise.all([getStoreNames(), getStoreTypes()])).map(arr =>
            arr.map(x => ({ key: x, name: x, selected: true }))
        );
    });
</script>

<menu>
    <ButtonGroup bind:options={shops} />
    <ButtonGroup bind:options={markets} />
    <button class:selected={show_hidden} on:click={() => (show_hidden = !show_hidden)}>
        <img src="/eye-slash.svg" alt="Показать скрытые товары" />
    </button>
    <div class="spacer" />
    <Search placeholder="Поиск..." bind:value={search} />
</menu>

<style lang="scss">
    @use "mixins.scss" as *;
    menu {
        display: flex;
        gap: 16px;
        padding: 8px 12px;
    }

    button {
        @include selectable-button;
        padding: 4px;
        aspect-ratio: 1;
        border: 0;
        border-radius: 4px;

        &.selected {
            > img {
                filter: invert(1);
            }
        }
        > img {
            height: 24px;
            width: 24px;
        }
    }

    .spacer {
        margin-right: auto;
        margin-left: -16px;
    }
</style>
