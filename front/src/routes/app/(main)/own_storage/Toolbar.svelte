<script lang="ts" context="module">
    import { derived } from "svelte/store";

    export function getOwnStorageFilter() {
        return derived(filterState, state => {
            const FIELDS = ["name", "note_1", "note_2", "note_3"] as const;
            const sku = (data: OwnStorage) => data.offer.sku;
            const getters = FIELDS.map(
                field => (data: OwnStorage) => data.offer[field].map(x => x ?? "")
            );
            let searchFilter = createSearchFilter(state.search, [sku, ...getters]);

            return (storage: OwnStorage) =>
                searchFilter(storage) &&
                storage.offer.name_of_shop.some(shop =>
                    state.shops
                        .filter(x => x.selected)
                        .map(x => x.name)
                        .includes(shop)
                );
        });
    }
</script>

<script lang="ts">
    import Search from "$lib/filter/Search.svelte";
    import createSearchFilter from "$lib/filter/search";
    import MarketsFilter from "$lib/filter/ShopsFilter.svelte";
    import { filterState } from "../state";
    import type { OwnStorage } from "$lib/data/own_storage";
</script>

<menu>
    <MarketsFilter bind:options={$filterState.shops} />
    <Search bind:value={$filterState.search} placeholder="Поиск..." />
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
