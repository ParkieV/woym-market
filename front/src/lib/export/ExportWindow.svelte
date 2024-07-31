<script lang="ts">
    import Window from "../components/windows/Window.svelte";
    import { onMount } from "svelte";
    import { getStoreNames, getStoreTypes } from "$lib/data/markets";
    import { OwnStorageExport, SimpleExport, SupplyExport, ViolatorsExport } from ".";
    import { page } from "$app/stores";
    import { getStoragePlaces, type StoragePlace } from "$lib/data/own_storage/places";

    export let open: boolean;
    let data: SimpleExport | SupplyExport | null = null;
    $: if (open === false) data = null;

    const ok = async () => {
        if (data === null) return;
        let { ok } = await data.export();
        open = false;
    };

    let name_of_shop_options: string[] = [];
    let market_options: string[] = [];
    let storages: StoragePlace[] = [];

    onMount(async () => {
        [name_of_shop_options, market_options, storages] = await Promise.all([
            getStoreNames(),
            getStoreTypes(),
            getStoragePlaces()
        ]);
    });
</script>

<Window bind:open>
    <h1 slot="header">Экспорт</h1>
    <div>
        <label>
            <span>Вид</span>
            <select bind:value={data}>
                <option value={null} disabled>Не выбрано</option>
                <option value={new SimpleExport("data/export")}>Карточки: Таблица</option>
                <option value={new OwnStorageExport()}>Мои остатки: Таблица</option>
                <option value={new SimpleExport("stocks/fbo/export")}>FBO остатки: Таблица</option>
                <option value={new ViolatorsExport()}>Нарушители РРЦ</option>
                {#if $page.url.pathname === "/app/fbo_storage"}
                    <option value={new SupplyExport()}>Поставка</option>
                {/if}
            </select>
        </label>
        {#if data !== null}
            <label>
                <span>Маркет</span>
                <select bind:value={data.market}>
                    <option value={null}>Все</option>
                    {#each market_options as option}
                        <option value={option}>{option}</option>
                    {/each}
                </select>
            </label>
            <label>
                <span>Магазин</span>
                <select bind:value={data.name_of_shop}>
                    <option value={null}>Все</option>
                    {#each name_of_shop_options as option}
                        <option value={option}>{option}</option>
                    {/each}
                </select>
            </label>
            {#if data instanceof SupplyExport}
                <label>
                    <span>Режим</span>
                    <select bind:value={data.type}>
                        <option value={null}>Не выбрано</option>
                        <option value={"only-own-storage"}>Только Мой склад</option>
                        <option value={"only-stocks"}>Без учета Мой склад</option>
                        <option value={"with-own-storage"}>C учетом Мой склад</option>
                    </select>
                </label>
            {/if}
            {#if (data instanceof SupplyExport && data.isPlaceNeeded) || data instanceof OwnStorageExport}
                <label>
                    <span>Склад</span>
                    <select bind:value={data.place_id}>
                        <option value={null}>Не выбрано</option>
                        {#each storages as storage}
                            <option value={storage.id}>{storage.name}</option>
                        {/each}
                    </select>
                </label>
            {/if}
        {/if}
    </div>
    <svelte:fragment slot="footer">
        <button class="cancel" on:click={() => (open = false)}>Отмена</button>
        <button class="confirm" on:click={ok} disabled={!data || !data.valid}>Ок</button>
    </svelte:fragment>
</Window>

<style lang="scss">
    @use "mixins" as *;

    h1 {
        margin-bottom: 8px;
    }
    div {
        display: flex;
        flex-direction: column;
        gap: 12px;
        > label {
            display: flex;
            justify-content: space-between;
            border-bottom: 1px solid #b9b9b9;
            padding-bottom: 6px;
            > span,
            select {
                font-size: 16px;
            }
            > select {
                width: 300px;
                text-overflow: ellipsis;
                border-radius: 0;
                border: 0;
                background-color: transparent;
                text-align: end;
                padding-right: 4px;
            }
        }
    }

    button.confirm {
        @include primary-button;
        width: 80px;
    }
    button.cancel {
        @include secondary-button;
        width: 80px;
    }
</style>
