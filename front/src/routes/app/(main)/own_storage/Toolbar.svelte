<script lang="ts">
    import Search from "$lib/filter/Search.svelte";
    import MarketsFilter from "$lib/filter/ShopsFilter.svelte";
    import FilterButton from "$lib/filter/FilterButton.svelte";
    import { filterState } from "../state";
</script>

<menu>
    <MarketsFilter bind:options={$filterState.shops} />
    <Search bind:value={$filterState.search} placeholder="Поиск..." />
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
