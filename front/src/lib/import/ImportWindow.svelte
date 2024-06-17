<script lang="ts">
    import { createEventDispatcher, onMount } from "svelte";
    import Window from "../components/windows/Window.svelte";
    import { Import, SimpleImport, FboAdditionsImport } from ".";
    import Simple from "./Simple.svelte";
    import Warehouse from "./Warehouse.svelte";

    export let open: boolean;

    let data: Import | null = null;
    $: if (!open) data = null;

    const ok = async () => {
        if (data === null) return;
        let { ok } = await data.import();
        if (ok) dispatch("import");
        open = false;
    };

    let dispatch = createEventDispatcher<{ import: void }>();
</script>

<Window bind:open>
    <h1 slot="header">Импорт</h1>
    <div>
        <label>
            <span>Вид</span>
            <select bind:value={data}>
                <option value={null} disabled>Не выбрано</option>
                <option value={new SimpleImport("data/import", "table")}>Таблица</option>
                <option value={new SimpleImport("data/import", "sizes")}>Размеры</option>
                <option value={new SimpleImport("data/import", "prices")}>Цены</option>
                <option value={new SimpleImport("stocks/own-storage/import")}>Мои остатки</option>
                <option value={new SimpleImport("stocks/fbo/import")}>FBO остатки</option>
                <option value={new FboAdditionsImport()}>FBO Яндекс</option>
            </select>
        </label>
        {#if data instanceof SimpleImport}
            <Simple bind:data />
        {:else if data instanceof FboAdditionsImport}
            <Warehouse bind:data />
        {/if}
    </div>
    <svelte:fragment slot="footer">
        <button class="cancel" on:click={() => (open = false)}>Отмена</button>
        <button class="confirm" on:click={ok} disabled={!data || !data.valid}>Ок</button>
    </svelte:fragment>
</Window>

<style lang="scss">
    @use "mixins" as *;

    @import "./style.scss";
    @include import-inputs;

    h1 {
        margin-bottom: 8px;
    }
    div {
        display: flex;
        flex-direction: column;
        gap: 12px;
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
