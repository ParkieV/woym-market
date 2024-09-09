<script lang="ts">
    import { getStores, getStoreTypes, type Market } from "$lib/data/markets";
    import { onMount } from "svelte";
    import type { OffersImport } from ".";

    export let data: OffersImport;

    let markets: Promise<string[]> = Promise.resolve([]);
    let shops: Promise<Market[]> = Promise.resolve([]);

    onMount(() => {
        markets = getStoreTypes();
        shops = getStores();
    });
</script>

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
                <option value={shop.name}>{shop.name} ({shop.type})</option>
            {/each}
        {/await}
    </select>
</label>

<style lang="scss">
    @import "./style.scss";
    @include import-inputs;
</style>
