<script lang="ts">
    import ButtonGroup from "$lib/components/ButtonGroup.svelte";
    import Search from "$lib/components/Search.svelte";
    import type { Offer } from "$lib/data/offers";
    import { createEventDispatcher, onMount } from "svelte";

    let shops = new Set([
        { name: "CALMAR.SHOP", selected: true },
        { name: "MASTERSKRAB", selected: true }
    ]);
    let markets = new Set([
        { key: "yandex", name: "Яндекс", selected: true },
        { key: "ozon", name: "Озон", selected: true }
    ]);
    let search = "";
    let show_hidden: boolean = false;

    /** Fields that are compared to search query.*/
    const SEARCH_FIELDS = ["sku", "name", "note_1", "note_2", "note_3"] as const;

    function filter(offer: Offer): boolean {
        if (offer.hidden && !show_hidden) {
            return false;
        }
        for (const option of shops) {
            if (option.name == offer.name_of_shop && !option.selected) {
                return false;
            }
        }
        for (const option of markets) {
            if (option.key == offer.market && !option.selected) {
                return false;
            }
        }
        const _search = search.trim().toLowerCase().replaceAll("ё", "е");
        for (const key of SEARCH_FIELDS) {
            let val = offer[key];
            if (val === undefined || val === null) continue;
            val = val.trim().toLowerCase().replaceAll("ё", "е");
            if (val.includes(_search)) {
                return true;
            }
        }
        return false;
    }

    let dispatch = createEventDispatcher<{ filterChanged: (offer: Offer) => boolean }>();
    $: {
        search;
        shops;
        markets;
        show_hidden;
        dispatch("filterChanged", filter);
    }

    onMount(() => {
        dispatch("filterChanged", filter);
    })
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
