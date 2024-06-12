<script lang="ts">
    import { getStoreNames } from "$lib/data/markets";
    import { fetchJSON } from "$lib/fetch";
    import { onMount } from "svelte";
    import type WarehouseImport from "./warehouse";
    import SelectionBox from "$lib/components/SelectionBox.svelte";

    export let data: WarehouseImport;

    let shops: Promise<string[]> = Promise.resolve([]);
    let warehouses: Promise<Warehouse[]> = Promise.resolve([]);

    onMount(() => {
        shops = getStoreNames("yandex");
        warehouses = fetchJSON<{ warehouses: Warehouse[] }>("stocks/fbo/import/choices").then(
            x => x.data.warehouses
        );
    });

    type Warehouse = { id: number; name: string };
</script>

<label>
    <span>Магазин</span>
    <select bind:value={data.name_of_shop}>
        <option value={null} disabled>Не выбрано</option>
        {#await shops then shops}
            {#each shops as shop}
                <option value={shop}>{shop}</option>
            {/each}
        {/await}
    </select>
</label>
<section>
    <span>Склад</span>
    <SelectionBox bind:selectedId={data.warehouse_id} data={warehouses} let:value>
        <span>{value.name}</span>
    </SelectionBox>
</section>

<style lang="scss">
    @import "./style.scss";
    @include import-inputs;

    section {
        display: contents;
        > span {
            @include underline();
        }
    }
</style>
