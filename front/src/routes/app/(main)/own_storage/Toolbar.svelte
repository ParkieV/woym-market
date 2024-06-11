<script lang="ts">
    import type { Filter } from "$lib/components/datagrid/filters";
    import FilterGroup from "$lib/components/datagrid/filters/FilterGroup.svelte";
    import OptionsFilter, {
        type Option
    } from "$lib/components/datagrid/filters/OptionsFilter.svelte";
    import Search from "$lib/components/datagrid/filters/Search.svelte";
    import type { OwnStorage } from "$lib/data/own_storage";

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

    const market_filter = (storage: OwnStorage, opts: Option[]) =>
        storage.name_of_shop.some(shop =>
            opts
                .filter(x => x.selected)
                .map(x => x.name)
                .includes(shop)
        );

    export let filter: Filter<OwnStorage>;
</script>

<menu>
    <FilterGroup bind:filter>
        <div class="stores">
            <FilterGroup kind="or">
                <OptionsFilter filter={market_filter} image={"/yandex.svg"} bind:options={yandex} />
                <OptionsFilter filter={market_filter} image={"/ozon.svg"} bind:options={ozon} />
            </FilterGroup>
        </div>
        <Search placeholder="Поиск..." fields={SEARCH_FIELDS} />
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
