<script lang="ts">
    import { createEventDispatcher, onMount } from "svelte";
    import Window from "../components/windows/Window.svelte";
    import { getStoreNames, getStoreTypes } from "$lib/data/markets";
    import Import from ".";
    import SimpleImport from "./simple";
    import WarehouseImport from "./warehouse";
    import Simple from "./Simple.svelte";
    import Warehouse from "./Warehouse.svelte";

    export let open: boolean;
    let data: Import = new SimpleImport();

    const ok = async () => {
        let { ok } = await data.import();
        if (ok) dispatch("import");
        open = false;
    };

    const change = () => {
        let newData: Import;
        if (SimpleImport.matchKind(data.kind)) {
            newData = new SimpleImport();
        } else if (WarehouseImport.matchKind(data.kind)) {
            newData = new WarehouseImport();
        } else {
            throw new Error("Необработанный вид импорта.");
        }

        if (data.constructor !== newData.constructor) {
            newData.kind = data.kind;
            data = newData;
        }
    };

    let dispatch = createEventDispatcher<{ import: void }>();
</script>

<Window bind:open>
    <h1 slot="header">Импорт</h1>
    <div>
        <label>
            <span>Вид</span>
            <select bind:value={data.kind} on:change={change}>
                <option value="table">Таблица</option>
                <option value="sizes">Размеры</option>
                <option value="prices">Цены</option>
                <option value="matrix-fbo-stocks">FBO остатки</option>
                <option value="matrix-own-storage">Свои остатки</option>
                <option value="fbo-yandex">FBO Яндекс</option>
            </select>
        </label>
        {#if data instanceof SimpleImport}
            <Simple bind:data />
        {:else if data instanceof WarehouseImport}
            <Warehouse bind:data />
        {/if}
    </div>
    <svelte:fragment slot="footer">
        <button class="cancel" on:click={() => (open = false)}>Отмена</button>
        <button class="confirm" on:click={ok} disabled={!data.valid}>Ок</button>
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
