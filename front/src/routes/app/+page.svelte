<script lang="ts">
    import { goto } from "$app/navigation";
    import Search from "$lib/Search.svelte";
    import { fetchAuthenticated, logout } from "$lib/auth";
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

    async function export_excel() {
        let blob = await (await fetchAuthenticated("offers/xlsx")).blob();
        let url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = "report.xlsx";
        link.click();
    }

    async function import_excel() {
        const input = document.createElement("input");
        input.type = "file";
        input.onchange = async e => {
            let target = e.target as HTMLInputElement;
            let file = target.files![0];
            let formData = new FormData();
            formData.append("data", file);
            let responce = await fetchAuthenticated("offers/xlsx", {
                method: "POST",
                body: formData,
            });
            if (!responce.ok)
            {
                alert("Импорт не удался");
            }
        };
        input.click();
    }
</script>

 <!-- TODO: ConfirmationDialog when data is updated -->
<!-- <ConfirmationDialog open={true} text="Это действие обновит 100500 строк."/> -->
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
