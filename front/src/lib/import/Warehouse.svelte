<script lang="ts">
    import { getStoreNames } from "$lib/data/markets";
    import { onMount } from "svelte";
    import SelectionBox from "$lib/components/SelectionBox.svelte";
    import { getWarehouses, type Warehouse } from "$lib/data/warehouse";
    import type { FboAdditionsImport } from ".";

    export let data: FboAdditionsImport;

    let shops: Promise<string[]> = Promise.resolve([]);
    let warehouses: Promise<Warehouse[]> = Promise.resolve([]);

    onMount(() => {
        shops = getStoreNames("yandex");
        warehouses = getWarehouses().then(warehouse =>
            warehouse
                .filter(({ market }) => market === "yandex")
                .sort((a, b) => a.name.localeCompare(b.name))
        );
    });
</script>

<label>
    <span>Магазин</span>
    <select bind:value={data.props.name_of_shop}>
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
    <SelectionBox bind:selectedId={data.props.warehouse_id} data={warehouses} let:value>
        <li
            title={`${value.name}, ${
                value.from_file_updated_at
                    ? new Date(value.from_file_updated_at).toLocaleString()
                    : "не загружался"
            }`}
        >
            <div>{value.name}</div>
            {#if value.from_file_updated_at !== null}
                <span>
                    {new Date(value.from_file_updated_at).toLocaleDateString()}
                </span>
            {/if}
        </li>
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

    li {
        display: flex;
        justify-content: space-between;
        gap: 20px;
        list-style: none;
        width: 100%;
        > div {
            font-size: 14px;
            &:first-child {
                flex: 1;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }
            &:last-child {
                flex: 0 0 content;
            }
        }
    }
</style>
