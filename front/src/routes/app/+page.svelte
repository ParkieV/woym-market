<script lang="ts">
    import { goto } from "$app/navigation";
    import Search from "$lib/Search.svelte";
    import { Logout } from "$lib/auth";
    import { createGrid } from "ag-grid-community";
    import { onMount } from "svelte";
    import type { PageData } from "./$types";
    import { DataGridOptions } from "$lib/datagrid/offers";
    import Sidebar from "./Sidebar.svelte";
    import ImageModal from "./ImageModal.svelte";
    import SettingsDialog from "./SettingsDialog.svelte";

    export let data: PageData;
    let settings_open: boolean = false;
    let selected_image = "";

    onMount(() => {
        const gridElement = document.querySelector("#grid")! as HTMLElement;
        const options = DataGridOptions(src => {
            selected_image = src;
        });
        options.rowData = data.offers;
        let grid = createGrid(gridElement, options);
    });

    function SignOut() {
        Logout();
        goto("/auth");
    }
</script>

<ImageModal bind:src={selected_image} />
<SettingsDialog bind:open={settings_open} />

<div id="wrapper">
    <Sidebar
        on:settings={() => (settings_open = true)}
        on:exit={() => {
            logout();
            goto("/auth");
        }}
    />
    <main>
        <menu class="toolbar">
            <button on:click={export_excel}>Экспорт</button>
            <button on:click={import_excel}>Импорт</button>
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
