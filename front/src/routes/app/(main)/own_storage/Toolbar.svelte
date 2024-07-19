<script lang="ts">
    import type { Filter } from "$lib/datagrid/filters";
    import FilterGroup from "$lib/datagrid/filters/FilterGroup.svelte";
    import OptionsFilter, { type Option } from "$lib/datagrid/filters/OptionsFilter.svelte";
    import Search from "$lib/datagrid/filters/Search.svelte";
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

    const market_filter = (storage: OwnStorage, opts: Option[]) => {
        return storage.offer.name_of_shop.some(shop =>
            opts
                .filter(x => x.selected)
                .map(x => x.name)
                .includes(shop)
        );
    };

    function searchStrings(data: OwnStorage) {
        return [
            data.offer.sku,
            data.offer.name,
            data.offer.note_1,
            data.offer.note_2,
            data.offer.note_3
        ]
            .flat(1)
            .filter(x => x !== null) as string[];
    }

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
        <Search placeholder="Поиск..." fields={searchStrings} />
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
