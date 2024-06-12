<script lang="ts">
    import type { Filter } from "$lib/datagrid/filters";
    import BinaryFilter from "$lib/datagrid/filters/BinaryFilter.svelte";
    import FilterGroup from "$lib/datagrid/filters/FilterGroup.svelte";
    import OptionsFilter, { type Option } from "$lib/datagrid/filters/OptionsFilter.svelte";
    import Search from "$lib/datagrid/filters/Search.svelte";
    import TernaryFilter from "$lib/datagrid/filters/TernaryFilter.svelte";
    import type { FboStocks } from "$lib/data/fbo_storage";

    export let markets: {
        id: number;
        name: string;
        type: string;
    }[];

    let yandex = markets
        .filter(({ type }) => type === "yandex")
        .map(({ name }) => ({ name, selected: true }));
    let ozon = markets
        .filter(({ type }) => type === "ozon")
        .map(({ name }) => ({ name, selected: true }));
    const SEARCH_FIELDS = ["sku", "name", "note_1", "note_2", "note_3"];

    const market_filter = (storage: FboStocks, opts: Option[]) =>
        opts.every(({ name, selected }) => selected || name !== storage.name_of_shop);
    const hidden_filter = (storage: FboStocks) => !storage.hidden;
    const available_filter = (storage: FboStocks) => storage.supplier_available;

    export let filter: Filter<FboStocks>;
</script>

<menu>
    <FilterGroup bind:filter>
        <div class="stores">
            <OptionsFilter filter={market_filter} image={"/yandex.svg"} bind:options={yandex} />
            <OptionsFilter filter={market_filter} image={"/ozon.svg"} bind:options={ozon} />
        </div>
        <Search placeholder="Поиск..." fields={SEARCH_FIELDS} />
        <TernaryFilter
            filter={available_filter}
            image={"/package.svg"}
            alt="Наличие у поставщика"
        />
        <BinaryFilter
            filter={hidden_filter}
            mode="disable"
            image={"/eye-slash.svg"}
            alt="Отображать скрытые"
        />
    </FilterGroup>
</menu>

<style lang="scss">
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
    }
</style>
