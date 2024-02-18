<script lang="ts">
    import { downloadFile } from "$lib/util";
    import Window from "./Window.svelte";
    import { handleRequest } from "$lib";
    import { fetchAuthenticated } from "$lib/auth";

    type Params = {
        export_type: "table" | "matrix-fbo-stocks" | "matrix-own-storage";
        market?: "ozon" | "yandex";
        name_of_shop?: "CALMAR.SHOP" | "MASTERSKRAB";
    };

    export let open: boolean;
    let data: Params = { export_type: "table" };

    const ok = () => {
        for (const key in data) {
            if (data[key as keyof Params] === undefined) {
                delete data[key as keyof Params];
            }
        }
        let url = "data/export?" + new URLSearchParams(data);

        let promise = fetchAuthenticated(url);
        handleRequest(promise, {
            header: "Скачивание файла...",
            errorHeader: "Ошибка экспорта",
            onSuccess: async response => {
                let blob = await response.blob();
                downloadFile(blob, "report.xlsx");
            }
        });

        open = false;
    };
</script>

<Window bind:open>
    <h1 slot="header">Экспорт</h1>
    <div>
        <label>
            <span>Вид</span>
            <select bind:value={data.export_type}>
                <option value="table">Таблица</option>
                <option value="matrix-fbo-stocks">FBO остатки</option>
                <option value="matrix-own-storage">Свои остатков</option>
            </select>
        </label>
        <label>
            <span>Маркет</span>
            <select bind:value={data.market}>
                <option value={undefined}>Все</option>
                <option value="yandex">Яндекс</option>
                <option value="ozon">Озон</option>
            </select>
        </label>
        <label>
            <span>Магазин</span>
            <select bind:value={data.name_of_shop}>
                <option value={undefined}>Все</option>
                <option value="CALMAR.SHOP">CALMAR.SHOP</option>
                <option value="MASTERSKRAB">MASTERSKRAB</option>
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
