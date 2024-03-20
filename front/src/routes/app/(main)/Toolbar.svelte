<script lang="ts">
    import ButtonGroup from "$lib/components/ButtonGroup.svelte";
    import Search from "$lib/components/Search.svelte";
    import { getStoreNames, getStoreTypes } from "$lib/data/markets";
    import type { FilterParams } from "$lib/grid/filters";
    import { createEventDispatcher, onMount } from "svelte";

    export let options: {
        id: number;
        name: string;
        type: string;
    }[];

    let yandex = options
        .filter(x => x.type === "yandex")
        .map(({ name }) => ({ key: name, name, selected: true }));
    let ozon = options
        .filter(x => x.type === "ozon")
        .map(({ name }) => ({ key: name, name, selected: true }));
    let search = "";
    let show_hidden: boolean = false;

    let dispatch = createEventDispatcher<{ filterChanged: FilterParams }>();
    $: {
        search, yandex, ozon, show_hidden;
        dispatch("filterChanged", { stores: [...yandex, ...ozon], search, show_hidden });
    }
</script>

<menu>
    <div class="stores">
        <ButtonGroup image={"/yandex-market.svg"} bind:options={yandex} />
        <ButtonGroup image={"/ozon.svg"} bind:options={ozon} />
    </div>
    <Search placeholder="Поиск..." bind:value={search} />
    <button class:selected={show_hidden} on:click={() => (show_hidden = !show_hidden)}>
        <img src="/eye-slash.svg" alt="Показать скрытые товары" />
    </button>
</menu>

<style lang="scss">
    @use "mixins.scss" as *;
    menu {
        display: flex;
        gap: 12px;
        padding: 8px 12px;
        width: 100%;
        overflow: hidden;

        > .stores {
            flex: 1 1 400px;
            display: flex;
            gap: 16px;
            overflow-x: scroll;
            margin-right: auto;
        }

        > button {
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
    }
</style>
