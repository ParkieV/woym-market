<script lang="ts">
    import Grid from "./Grid.svelte";
    import { getContext, onMount } from "svelte";
    import { patchOfferList, OffersData, type Offer } from "$lib/data/offers";
    import { fetchLogs } from "$lib/data/settings";
    import type { ModalKind } from "./Modals.svelte";
    import { ChangeList } from "$lib/datagrid/changes";
    import Toolbar from "./Toolbar.svelte";
    import ImageWindow from "$lib/windows/ImageWindow.svelte";
    import ImportWindow from "$lib/windows/ImportWindow.svelte";
    import ExportWindow from "$lib/windows/ExportWindow.svelte";

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
    let import_open = false;
    let export_open = false;

    let updated_at: Date | null = null;

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

    let filter: (offer: Offer) => boolean = () => true;
</script>

<ImageWindow bind:src={selected_image} />
<ImportWindow bind:open={import_open} on:imported={refreshData} />
<ExportWindow bind:open={export_open} />
<main>
    <header>
        <menu class="menu">
            <button on:click={() => (export_open = true)}>Экспорт</button>
            <button on:click={() => (import_open = true)}>Импорт</button>
        </menu>
        <Toolbar
            on:filterChanged={e => {
                filter = e.detail;
            }}
        />
    </header>
    <Grid bind:data bind:changes bind:filter on:photoClicked={e => (selected_image = e.detail)} />
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
    @use "mixins" as *;

    main {
        display: flex;
        flex-direction: column;
        flex: 1;
    }

    header {
        display: flex;
        flex-direction: column;
        gap: 2px;
        .menu {
            display: flex;
            background-color: #f1f0f0;
            > button {
                background-color: transparent;
                border: 0;
                padding: 4px 12px;
                border-radius: 0;
                font-size: 15px;
                &:hover {
                    background-color: #e2e2e2;
                }
            }
        }
    }

    .bottombar {
        display: flex;
        align-items: center;
        padding: 16px;
        gap: 16px;
        button {
            padding-left: 16px;
            padding-right: 16px;
            height: 40px;
            &.confirm {
                @include primary-button;
            }
            &.cancel {
                @include secondary-button;
            }
            &:disabled,
            &:disabled:hover {
                color: white;
                background-color: #747474;
            }
        }
        > span {
            font-size: 16px;
            white-space: pre-wrap;
        }
    }
</style>
