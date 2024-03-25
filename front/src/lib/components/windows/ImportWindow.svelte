<script lang="ts">
    import { uploadFile } from "$lib/util";
    import { createEventDispatcher, onMount } from "svelte";
    import Window from "./Window.svelte";
    import { getStoreNames, getStoreTypes } from "$lib/data/markets";
    import { fetchPlain } from "$lib/fetch";
    import { showFetchModals } from "$lib/modal";

    type Params = {
        import_type: "table" | "sizes" | "prices" | "matrix-fbo-stocks" | "matrix-own-storage";
        market?: string;
        name_of_shop?: string;
    };

    export let open: boolean;
    let data: Params = { import_type: "table" };

    const ok = async () => {
        if (data.name_of_shop === undefined) {
            delete data.name_of_shop;
        }
        let blob = await uploadFile();
        let formData = new FormData();
        formData.append("data", blob);

        for (const key in data) {
            if (data[key as keyof Params] === undefined) {
                delete data[key as keyof Params];
            }
        }
        let url = "data/import?" + new URLSearchParams(data);

        let promise = fetchPlain(url, {
            method: "POST",
            body: formData
        });
        showFetchModals(promise, "Отправка файла...", "Ошибка импорта");
        promise.then(response => {
            if (response.ok) dispatch("import");
        });

        open = false;
    };

    let dispatch = createEventDispatcher<{ import: void }>();

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
    <h1 slot="header">Импорт</h1>
    <div>
        <label>
            <span>Вид</span>
            <select bind:value={data.import_type}>
                <option value="table">Таблица</option>
                <option value="sizes">Размеры</option>
                <option value="prices">Цены</option>
                <option value="matrix-fbo-stocks">FBO остатки</option>
                <option value="matrix-own-storage">Свои остатки</option>
            </select>
        </label>
        <label>
            <span>Маркет</span>
            <select bind:value={data.market}>
                <option value={undefined}>Все</option>
                {#each market_options as option}
                    <option value={option}>{option}</option>
                {/each}
            </select>
        </label>
        <label>
            <span>Магазин</span>
            <select bind:value={data.name_of_shop}>
                <option value={undefined}>Все</option>
                {#each name_of_shop_options as option}
                    <option value={option}>{option}</option>
                {/each}
            </select>
        </label>
    </div>
    <svelte:fragment slot="footer">
        <button class="cancel" on:click={() => (open = false)}>Отмена</button>
        <button class="confirm" on:click={ok}>Ок</button>
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
