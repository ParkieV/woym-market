<script lang="ts" context="module">
    import { derived } from "svelte/store";
    import type { Offer } from "$lib/data/offers";
    import { filterState } from "../state";

    export function getOffersFilter() {
        return derived(filterState, state => {
            const SEARCH_FIELDS = ["sku", "name", "note_1", "note_2", "note_3"] as const;
            let searchFilter = createSearchFilter(state.search, SEARCH_FIELDS);

            return (offer: Offer) =>
                searchFilter(offer) &&
                (state.supplierAvailable === null ||
                    state.supplierAvailable === offer.supplier_available) &&
                (!offer.hidden || state.showHidden) &&
                state.shops
                    .filter(x => x.selected)
                    .map(x => x.name)
                    .includes(offer.name_of_shop) &&
                state.shops
                    .filter(x => x.selected)
                    .map(x => x.market)
                    .includes(offer.market);
        });
    }
</script>

<script lang="ts">
    import BinaryFilter from "$lib/filter/BinaryFilter.svelte";
    import Search from "$lib/filter/Search.svelte";
    import TernaryFilter from "$lib/filter/TernaryFilter.svelte";
    import createSearchFilter from "$lib/filter/search";
    import ShopsFilter from "$lib/filter/ShopsFilter.svelte";
    import FilterButton from "$lib/filter/FilterButton.svelte";
</script>

<menu>
    <ShopsFilter bind:options={$filterState.shops} />
    <Search bind:value={$filterState.search} placeholder="Поиск..." />
    <TernaryFilter
        bind:value={$filterState.supplierAvailable}
        image={"/package.svg"}
        alt="Наличие у поставщика"
    />
    <BinaryFilter
        bind:value={$filterState.showHidden}
        image={"/eye-slash.svg"}
        alt="Отображать скрытые"
    />
    <FilterButton
        on:click={() => filterState.reset()}
        image={"/resetFilter.svg"}
        alt="Сбросить фильтры"
    />
</menu>

<style lang="scss">
    menu {
        display: flex;
        gap: 12px;
        padding: 8px 12px;
        width: 100%;
        overflow: hidden;
    }
</style>
