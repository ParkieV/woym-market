<script lang="ts">
    import { fetchAuthenticated } from "$lib/auth";
    import { downloadFile } from "$lib/util";
    import { getContext } from "svelte";
    import Window from "./Window.svelte";
    import type { ModalKind } from "../../routes/app/Modals.svelte";

    type Data = {
        market: "ozon" | "yandex" | "all";
        export_type: "table" | "matrix-offers" | "matrix-stocks";
        name_of_shop?: "CALMAR.SHOP" | "MASTERSKRAB";
    };

    export let open: boolean;
    let data: Data = {
        market: "all",
        export_type: "table"
    };

    const addModal = getContext<(modal: ModalKind) => void>("addModal");

    const ok = () => {
        if (data.name_of_shop === undefined) {
            delete data.name_of_shop;
        }
        let url = "offers/xlsx?" + new URLSearchParams(data);

        let promise = fetchAuthenticated(url);
        open = false;

        promise.then(async response => {
            let blob = await response.blob();
            downloadFile(blob, "report.xlsx");
        });

        addModal({
            kind: "await",
            promise,
            header: "Скачивание файла экспорта...",
            errorHeader: "Ошибка экспорта"
        });
    };
</script>

<Window bind:open>
    <h1 slot="header">Экспорт</h1>
    <div>
        <label>
            <span>Маркет</span>
            <select bind:value={data.market}>
                <option value="all">Все</option>
                <option value="yandex">Яндекс</option>
                <option value="ozon">Озон</option>
            </select>
        </label>
        <label>
            <span>Вид экспорта</span>
            <select bind:value={data.export_type}>
                <option value="table">Таблица</option>
                <option value="matrix-offers">Матрица товаров</option>
                <option value="matrix-stocks">Матрица остатков</option>
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
        padding-left: 24px;
        padding-right: 24px;
    }
    button.cancel {
        @include secondary-button;
    }
</style>
