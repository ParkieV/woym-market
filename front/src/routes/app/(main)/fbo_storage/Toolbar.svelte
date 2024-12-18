<script lang="ts">
    import BinaryFilter from "$lib/filter/BinaryFilter.svelte";
    import TernaryFilter from "$lib/filter/TernaryFilter.svelte";
    import Search from "$lib/filter/Search.svelte";
    import ShopsFilter from "$lib/filter/ShopsFilter.svelte";
    import FilterButton from "$lib/filter/FilterButton.svelte";
    import { filterState } from "../state";
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
