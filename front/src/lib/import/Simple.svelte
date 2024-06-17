<script lang="ts">
    import { getStoreNames, getStoreTypes } from "$lib/data/markets";
    import { onMount } from "svelte";
    import type { SimpleImport } from ".";

    export let data: SimpleImport;

    let markets: Promise<string[]> = Promise.resolve([]);
    let shops: Promise<string[]> = Promise.resolve([]);

    onMount(() => {
        markets = getStoreTypes();
        shops = getStoreNames();
    });
</script>

<label>
    <span>Маркет</span>
    <select bind:value={data.props.market}>
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
    <select bind:value={data.props.name_of_shop}>
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
