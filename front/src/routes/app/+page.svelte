<script lang="ts">
    import Search from "$lib/Search.svelte";
    import { fetchAuthenticated } from "$lib/auth";
    import ImageModal from "./ImageModal.svelte";
    import Grid from "./Grid.svelte";
    import { getContext, onMount } from "svelte";
    import { downloadFile, uploadFile } from "$lib/util";
    import { patchOfferList, OffersData, type Offer } from "$lib/data/offers";
    import { fetchLogs } from "$lib/data/logs";
    import type { ModalKind } from "./Modals.svelte";
    import { ChangeList } from "$lib/datagrid/changes";

    let data = new OffersData();
    let changes = new ChangeList<Offer, "sku">();

    const addModal = getContext<(modal: ModalKind) => void>("addModal");

    export function confirmChangesLoss(confirmed: () => void) {
        if (changes.hasChanges) {
            addModal({
                kind: "confirmChangesLoss",
                changed: changes.count,
                onConfirm: confirmed
            });
        } else {
            confirmed();
        }
    }

    let selected_image = "";
    let search = "";

    let updated_at: Date | null = null;

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
        addModal({
            kind: "confirmSave",
            onConfirm: async () => {
                await patchOfferList(data.offers.filter(x => changes.isChanged(x.sku)));
                await refreshData();
            }
        });
    }

    /** Refreshes data displayed in the grid. */
    async function refreshData() {
        changes.clear();
        changes = changes;

        await data.update();
        data = data;
    }

    onMount(() => {
        refreshData();
        let fetchDate = async () => {
            let logs = await fetchLogs();
            if (!logs.updated_at) return;
            let new_updated_at = new Date(logs.updated_at);

            if (updated_at === null) {
                updated_at = new_updated_at;
            } else if (updated_at < new_updated_at) {
                updated_at = new_updated_at;
                addModal({ kind: "dataUpdatedOnServer" });
                await refreshData();
            }
        };
        fetchDate();
        setInterval(fetchDate, 15 * 1000);
    });
</script>

<ImageModal bind:src={selected_image} />
<main>
    <menu class="toolbar">
        <button on:click={exportXlsx}>Экспорт</button>
        <button on:click={importXlsx}>Импорт</button>
        <div style="flex: 1;" />
        <Search placeholder="Поиск..." bind:value={search} />
    </menu>
    <Grid bind:data bind:changes bind:search on:photoClicked={e => (selected_image = e.detail)} />
    <menu class="bottombar">
        <span
            >{`Последнее обновление:\n${
                updated_at ? updated_at.toLocaleString("en-GB") : "N/A"
            }`}</span
        >
        <div style:flex="1" />
        <button class="cancel" on:click={cancelEdits} disabled={!changes.hasChanges}>
            Отмена
        </button>
        <button class="confirm" on:click={confirmSave} disabled={!changes.hasChanges}>
            Сохранить изменения
        </button>
    </menu>
</main>

<style lang="scss">
    main {
        display: flex;
        flex-direction: column;
        flex: 1;
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
