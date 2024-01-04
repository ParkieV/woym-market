<script lang="ts">
    import { goto } from "$app/navigation";
    import Search from "$lib/Search.svelte";
    import { Logout } from "$lib/auth";
    import { createGrid } from "ag-grid-community";
    import { onMount } from "svelte";
    import type { PageData } from "./$types";
    import { DataGridOptions } from "$lib/datagrid/offers";

    export let data: PageData;

    onMount(() => {
        const myGridElement = document.querySelector("#grid")! as HTMLElement;
        const options = DataGridOptions(data.offers);
        let grid = createGrid(myGridElement, options);
    });

    function SignOut() {
        Logout();
        goto("/auth");
    }
</script>

<div id="wrapper">
    <nav>
        <h1>mp-auto-price</h1>
        <div style="flex: 1;" />
        <button>Настройки</button>
        <button class="sign-out" on:click={SignOut}>
            <img src="sign-out.svg" alt="" />
            <span>Выход</span>
        </button>
    </nav>
    <main>
        <menu class="toolbar">
            <button>Импорт</button>
            <button>Экспорт</button>
            <div style="flex: 1;" />
            <Search placeholder="Поиск..." />
        </menu>
        <div id="grid" class="ag-theme-quartz"></div>
        <menu class="buttons">
            <button class="cancel"> Отмена </button>
            <button class="confirm"> Подтвердить </button>
        </menu>
    </main>
</div>

<style lang="scss">
    #wrapper {
        display: flex;
        align-items: stretch;
        height: 100%;

        > main {
            display: flex;
            flex-direction: column;
            flex: 1;
            > menu {
                &.buttons {
                    display: flex;
                    padding: 20px;
                    justify-content: end;
                    gap: 20px;
                    > button {
                        padding: 0 20px;
                        height: 40px;
                        border: 0;
                        color: white;
                    }
                    > button.cancel {
                        background-color: #cc1821;
                    }
                    > button.confirm {
                        background-color: #25692e;
                    }
                }
            }
            #grid {
                flex: 1;
                height: 100%;
            }
        }
    }

    nav {
        display: flex;
        align-items: center;
        width: 160px;
        flex-direction: column;
        padding: 20px 10px 20px 10px;
        gap: 10px;

        color: white;
        background-color: #455561;
        > button {
            display: flex;
            justify-content: center;
            align-items: center;
            align-self: stretch;
            gap: 4px;
            color: white;
            background-color: transparent;
            padding: 10px 20px;
            border: none;
            > img {
                width: 16px;
                height: 16px;
                filter: invert(1);
            }
            &:hover {
                background-color: rgba(0, 0, 0, 0.2);
            }
        }
    }

    .toolbar {
        display: flex;
        padding: 10px;

        > button {
            background-color: transparent;
            border: none;
            padding: 10px 20px;
            &:hover {
                background-color: #dddddd;
            }
        }
    }

    button {
        border-radius: 4px;
    }
</style>
