<script lang="ts">
    import ButtonGroup from "$lib/components/ButtonGroup.svelte";
    import Search from "$lib/components/Search.svelte";
    import { getStoreNames, getStoreTypes } from "$lib/data/markets";
    import type { OwnStorage } from "$lib/data/own_storage";
    import { createEventDispatcher, onMount } from "svelte";

    let shops: { key: string; name: string; selected: boolean }[] = [];
    let markets: { key: string; name: string; selected: boolean }[] = [];
    let search = "";

    /** Fields that are compared to search query.*/
    const SEARCH_FIELDS = ["sku", "name", "note_1", "note_2", "note_3"] as const;

    function filter(storage: OwnStorage): boolean {
        if (!passesMarket(storage)) return false;
        if (!passesShop(storage)) return false;
        const _search = search.trim().toLowerCase().replaceAll("ё", "е");
        for (const key of SEARCH_FIELDS) {
            let vals = storage[key];
            if (!Array.isArray(vals)) vals = [vals];
            for (const val of vals) {
                if (val === undefined || val === null || val === "") continue;
                let _val = val.trim().toLowerCase().replaceAll("ё", "е");
                if (_val.includes(_search)) {
                    return true;
                }
            }
        }
        return false;
    }

    function passesMarket(storage: OwnStorage): boolean {
        if (markets.every(x => x.selected)) return true;
        return storage.market.some(val => {
            return markets
                .filter(x => x.selected)
                .map(x => x.key)
                .includes(val);
        });
    }

    function passesShop(storage: OwnStorage): boolean {
        if (shops.every(x => x.selected)) return true;
        return storage.name_of_shop.some(val => {
            return shops
                .filter(x => x.selected)
                .map(x => x.name)
                .includes(val);
        });
    }

    let dispatch = createEventDispatcher<{ filterChanged: (offer: OwnStorage) => boolean }>();
    $: {
        search;
        shops;
        markets;
        dispatch("filterChanged", filter);
    }

    onMount(async () => {
        [shops, markets] = (await Promise.all([getStoreNames(), getStoreTypes()])).map(arr =>
            arr.map(x => ({ key: x, name: x, selected: true }))
        );
        dispatch("filterChanged", filter);
    });
</script>

<menu>
    <ButtonGroup bind:options={shops} />
    <ButtonGroup bind:options={markets} />
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

    .spacer {
        margin-right: auto;
        margin-left: -16px;
    }
</style>
