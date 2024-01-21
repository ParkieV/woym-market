<script lang="ts">
    import { goto } from "$app/navigation";
    import Search from "$lib/Search.svelte";
    import { fetchAuthenticated, logout } from "$lib/auth";
    import Sidebar from "./Sidebar.svelte";
    import ImageModal from "./ImageModal.svelte";
    import SettingsDialog from "./SettingsDialog.svelte";
    import Grid from "./Grid.svelte";
    import { onMount } from "svelte";
    import { downloadFile, uploadFile } from "$lib/util";
    import { fetchOfferList, patchOfferList, type Offer } from "$lib/data/offers";
    import { fetchLogs } from "$lib/data/logs";
    import Modals from "./Modals.svelte";
    import type { ModalKind } from "./Modals.svelte";

    let changed: Map<string, Offer> = new Map();
    let data: "loading" | Offer[] = "loading";

    let modals: ModalKind[] = [];

    export function confirmChangesLoss(confirmed: () => void) {
        if (changed.size !== 0) {
            modals = [
                ...modals,
                {
                    kind: "confirmChangesLoss",
                    changed: changed.size,
                    onConfirm: confirmed
                }
            ];
        } else {
            confirmed();
        }
    }

    let settings_open: boolean = false;
    let selected_image = "";
    let search = "";

    let updated_at: Date | null;

    async function exportXlsx() {
        let blob = await (await fetchAuthenticated("offers/xlsx")).blob();
        downloadFile(blob, "report.xlsx");
    }

    async function importXlsx() {
        confirmChangesLoss(async () => {
            let blob = await uploadFile();
            let formData = new FormData();
            formData.append("data", blob);
            let responce = await fetchAuthenticated("offers/xlsx", {
                method: "POST",
                body: formData
            });
            if (!responce.ok) {
                alert("Импорт не удался");
            } else {
                await refreshData();
            }
        });
    }

    function cancelEdits() {
        confirmChangesLoss(async () => {
            await refreshData();
        });
    }

    async function confirmSave() {
        modals = [
            ...modals,
            {
                kind: "confirmSave",
                onConfirm: async () => {
                    let data = Array.from(changed.values());
                    await patchOfferList(data);
                    await refreshData();
                }
            }
        ];
    }

    /** Refreshes data displayed in the grid. */
    async function refreshData() {
        data = "loading";
        changed.clear();
        changed = changed;
        data = await fetchOfferList();
    }

    onMount(() => {
        refreshData();
        let fetchDate = async () => {
            let settings = await fetchLogs();
            let new_updated_at = settings.updated_at ? new Date(settings.updated_at) : null;
            if (new_updated_at === null) {
                return;
            }
            if (updated_at ? updated_at < new_updated_at : false) {
                modals = [...modals, { kind: "dataUpdatedOnServer" }];
                await refreshData();
            }
            updated_at = new_updated_at;
        };
        fetchDate();
        setInterval(fetchDate, 15 * 1000);
    });
</script>

<ImageModal bind:src={selected_image} />
<SettingsDialog bind:open={settings_open} on:confirm={() => refreshData()} />
<Modals bind:modals />

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
        <Grid
            bind:data
            bind:changed
            bind:search
            on:photoClicked={e => (selected_image = e.detail)}
        />
        <menu class="bottombar">
            <span
                >{`Последнее обновление:\n${
                    updated_at ? updated_at.toLocaleString("en-GB") : "N/A"
                }`}</span
            >
            <div style:flex="1" />
            <button class="cancel" on:click={cancelEdits} disabled={changed.size == 0}>
                Отмена
            </button>
            <button class="confirm" on:click={confirmSave} disabled={changed.size == 0}>
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
