<script lang="ts">
    import { getStoreNames, getStoreTypes } from "$lib/data/markets";
    import { onMount } from "svelte";
    import type { OwnStorageImport } from ".";
    import { getStoragePlaces, type StoragePlace } from "$lib/data/own_storage/places";

    export let data: OwnStorageImport;

    let markets: Promise<string[]> = Promise.resolve([]);
    let shops: Promise<string[]> = Promise.resolve([]);
    let storages: Promise<StoragePlace[]> = Promise.resolve([]);

    onMount(() => {
        markets = getStoreTypes();
        shops = getStoreNames();
        storages = getStoragePlaces();
    });
</script>

<label>
    <span>Склад</span>
    <select bind:value={data.place_id}>
        <option value={null}>Не выбрано</option>
        {#await storages then storages}
            {#each storages as storage}
                <option value={storage.id}>{storage.name}</option>
            {/each}
        {/await}
    </select>
</label>
<label>
    <span>Маркет</span>
    <select bind:value={data.market}>
        <option value={null}>Все</option>
        {#await markets then markets}
            {#each markets as market}
                <option value={market}>{market}</option>
            {/each}
        {/await}
    </select>
</label>
<label>
    <span>Магазин</span>
    <select bind:value={data.name_of_shop}>
        <option value={null}>Все</option>
        {#await shops then shops}
            {#each shops as shop}
                <option value={shop}>{shop}</option>
            {/each}
        {/await}
    </select>
</label>

<style lang="scss">
    @import "./style.scss";
    @include import-inputs;
</style>
