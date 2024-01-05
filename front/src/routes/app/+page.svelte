<script lang="ts">
    import { goto, invalidateAll } from "$app/navigation";
    import Search from "$lib/Search.svelte";
    import { fetchAuthenticated, logout } from "$lib/auth";
    import { GridApi, createGrid } from "ag-grid-community";
    import { onMount } from "svelte";
    import type { PageData } from "./$types";
    import { DataGridOptions } from "$lib/datagrid/offers";
    import Sidebar from "./Sidebar.svelte";
    import ImageModal from "./ImageModal.svelte";
    import SettingsDialog from "./SettingsDialog.svelte";
    import { patchOfferList, type Offer } from "$lib";

    export let data: PageData;

    let changed: Map<string, Offer> = new Map();
    let grid: GridApi;

    let settings_open: boolean = false;
    let selected_image = "";
    let search = "";
    let last_updated = new Date(0);

    $: if (grid) {
        search;
        grid.onFilterChanged();
    }

    onMount(() => {
        const gridElement = document.querySelector("#grid")! as HTMLElement;
        const options = DataGridOptions({
            changed,
            onPhotoClicked: src => (selected_image = src),
            isFilterEnabled: () => search != "",
            filter: e => {
                let _search = search.trim().toLowerCase().replaceAll("ё", "е");
                let name = e.data!.name.toLowerCase().replaceAll("ё", "е");
                let sku = e.data!.sku.toLowerCase().replaceAll("ё", "е");
                return name.includes(_search) || sku.includes(_search);
            },
            onChangedUpdated: () => {
                changed = changed;
            }
        });
        options.rowData = data.offers;
        grid = createGrid(gridElement, options);
    });

    async function exportXlsx() {
        let blob = await (await fetchAuthenticated("offers/xlsx")).blob();
        let url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = "report.xlsx";
        link.click();
    }

    async function importXlsx() {
        const input = document.createElement("input");
        input.type = "file";
        input.onchange = async e => {
            let target = e.target as HTMLInputElement;
            let file = target.files![0];
            let formData = new FormData();
            formData.append("data", file);
            let responce = await fetchAuthenticated("offers/xlsx", {
                method: "POST",
                body: formData
            });
            if (!responce.ok) {
                alert("Импорт не удался");
            } else {
                await reloadGrid();
            }
        };
        input.click();
    }

    async function cancel_edits() {
        await reloadGrid();
    }

    async function confirm_edits() {
        let data = Array.from(changed.values());
        await patchOfferList(data);
        await reloadGrid();
    }

    async function reloadGrid() {
        changed.clear();
        changed = changed;
        await invalidateAll();
        grid.setGridOption("rowData", data.offers);
    }

    async function refreshData() {
        if (
            changed.size == 0 ||
            confirm(`Вы внесли ${changed.size} изменений. Они будут потеряны, вы уверены?`) // TODO: use custom confirmation dialog
        ) {
            // TODO: implement after backend endpoint is completed.
            alert("Этот функционал в разработке!");
        }
    }
</script>

<!-- TODO: Show ConfirmationDialog before any dangerous action -->
<!-- <ConfirmationDialog open={true} text="Это действие обновит 100500 строк."/> -->
<ImageModal bind:src={selected_image} />
<SettingsDialog bind:open={settings_open} on:confirm={() => reloadGrid()} />

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
            <button on:click={exportXlsx}>Экспорт</button>
            <button on:click={importXlsx}>Импорт</button>
            <div style="flex: 1;" />
            <Search placeholder="Поиск..." bind:value={search} />
        </menu>
        <div id="grid" class="ag-theme-quartz"></div>
        <menu class="bottombar">
            <button on:click={refreshData} class="refresh"> Обновить данные </button>
            <span>{`Последнее обновление:\n${last_updated.toLocaleString("en-GB", {})}`}</span>
            <div style:flex="1" />
            <button class="cancel" on:click={cancel_edits} disabled={changed.size == 0}>
                Отмена
            </button>
            <button class="confirm" on:click={confirm_edits} disabled={changed.size == 0}>
                Сохранить изменения
            </button>
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

    .bottombar {
        display: flex;
        align-items: center;
        padding: 16px;
        gap: 16px;
        > button {
            padding: 0 16px;
            height: 40px;
            border: 0;
            color: white;
            &.refresh {
                background-color: #252525;
                &:hover {
                    background-color: #111111;
                }
            }
        }
        > span {
            font-size: 16px;
            white-space: pre-wrap;
        }
    }

    button {
        border-radius: 4px;
    }
</style>
