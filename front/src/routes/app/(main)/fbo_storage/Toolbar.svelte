<script lang="ts" context="module">
    export function getFboStorageFilter() {
        return derived(filterState, state => {
            const SEARCH_FIELDS = ["sku", "name", "note_1", "note_2", "note_3"] as const;
            let searchFilter = createSearchFilter(state.search, SEARCH_FIELDS);

            return (fboStorage: FboStorage) =>
                searchFilter(fboStorage) &&
                (state.supplierAvailable === null ||
                    state.supplierAvailable === fboStorage.supplier_available) &&
                (!fboStorage.hidden || state.showHidden) &&
                state.shops
                    .filter(x => x.selected)
                    .map(x => x.name)
                    .includes(fboStorage.name_of_shop) &&
                state.shops
                    .filter(x => x.selected)
                    .map(x => x.market)
                    .includes(fboStorage.market);
        });
    }
    export function getFboStocksFilter() {
        return derived(filterState, state => {
            return (stocks: FboStocks): boolean =>
                !state.hideUnmarkedWarehouses || get(fboStocksSelection.selected).has(stocks.id);
        });
    }
</script>

<script lang="ts">
    import BinaryFilter from "$lib/filter/BinaryFilter.svelte";
    import TernaryFilter from "$lib/filter/TernaryFilter.svelte";
    import Search from "$lib/filter/Search.svelte";
    import ShopsFilter from "$lib/filter/ShopsFilter.svelte";
    import { fboStocksSelection, filterState } from "../state";
    import { derived, get } from "svelte/store";
    import type { FboStocks, FboStorage } from "$lib/data/fbo_storage";
    import createSearchFilter from "$lib/filter/search";
    import FilterButton from "$lib/filter/FilterButton.svelte";
</script>

<menu>
    <ShopsFilter bind:options={$filterState.shops} />
    <Search bind:value={$filterState.search} placeholder="Поиск..." />
    <BinaryFilter
        bind:value={$filterState.hideUnmarkedWarehouses}
        image={"/list-checks.svg"}
        alt="Скрывать неотмеченные склады"
    />
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
