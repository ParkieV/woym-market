<script lang="ts">
    import { fetchAuthenticated } from "$lib/auth";
    import { uploadFile } from "$lib/util";
    import { createEventDispatcher } from "svelte";
    import Window from "./Window.svelte";

    type Data = {
        market: "ozon" | "yandex" | "all";
        import_type: "prices" | "sizes" | "table" | "matrix-stocks";
        name_of_shop?: "CALMAR.SHOP" | "MASTERSKRAB";
    };

    export let open: boolean;
    let data: Data = {
        market: "all",
        import_type: "table"
    };

    const ok = async () => {
        if (data.name_of_shop === undefined) {
            delete data.name_of_shop;
        }
        let blob = await uploadFile();
        let formData = new FormData();
        formData.append("data", blob);
        let url = "offers/xlsx?" + new URLSearchParams(data);
        let responce = await fetchAuthenticated(url, {
            method: "POST",
            body: formData
        });
        open = false;
        if (!responce.ok) {
            alert("Импорт не удался");
        } else {
            dispatch("imported");
        }
    };

    let dispatch = createEventDispatcher<{ imported: void }>();
</script>

<Window bind:open>
    <h1 slot="header">Импорт</h1>
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
            <span>Вид импорта</span>
            <select bind:value={data.import_type}>
                <option value="table">Таблица</option>
                <option value="prices">Цены</option>
                <option value="sizes">Размеры</option>
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
