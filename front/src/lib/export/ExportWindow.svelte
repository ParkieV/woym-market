<script lang="ts">
    import Window from "../components/windows/Window.svelte";
    import { onMount } from "svelte";
    import { getStoreNames, getStoreTypes } from "$lib/data/markets";
    import { SimpleExport, SupplyExport, ViolatorsExport } from ".";
    import { page } from "$app/stores";

    export let open: boolean;
    let data: SimpleExport | SupplyExport | null = null;
    $: if (open === false) data = null;
    $: if (data instanceof ViolatorsExport) data.market = "yandex";

    const ok = async () => {
        if (data === null) return;
        let { ok } = await data.export();
        open = false;
    };

    let name_of_shop_options: string[] = [];
    let market_options: string[] = [];
    onMount(async () => {
        [name_of_shop_options, market_options] = await Promise.all([
            getStoreNames(),
            getStoreTypes()
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
                <option value={new SimpleExport("data/export")}>Таблица</option>
                <option value={new SimpleExport("stocks/own-storage/export")}>Мои остатки</option>
                <option value={new SimpleExport("stocks/fbo/export")}>FBO остатки</option>
                <option value={new ViolatorsExport()}>Нарушители РРЦ</option>
                {#if $page.url.pathname === "/app/fbo_storage"}
                    <option value={new SupplyExport()}>Поставка</option>
                {/if}
            </select>
        </label>
        {#if data !== null}
            <label>
                <span>Маркет</span>
                <select bind:value={data.market} disabled={data instanceof ViolatorsExport}>
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
                width: 180px;
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
