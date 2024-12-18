<script lang="ts">
    import { filterState } from "../state";
    import BinaryFilter from "$lib/filter/BinaryFilter.svelte";
    import Search from "$lib/filter/Search.svelte";
    import TernaryFilter from "$lib/filter/TernaryFilter.svelte";
    import ShopsFilter from "$lib/filter/ShopsFilter.svelte";
    import FilterButton from "$lib/filter/FilterButton.svelte";
    import MultiFilter from "$lib/filter/MultiFilter.svelte";
</script>

<menu>
    <ShopsFilter bind:options={$filterState.shops} />
    <Search bind:value={$filterState.search} placeholder="Поиск..." />
    <TernaryFilter
        bind:value={$filterState.supplierAvailable}
        image={"/package.svg"}
        alt="Наличие у поставщика"
    />
    <MultiFilter
        bind:value={$filterState.attentionMarks}
        image={"/eyes.svg"}
        alt="Признаки внимания"
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
    }
</style>
