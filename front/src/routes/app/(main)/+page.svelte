<script lang="ts">
    import Grid from "$lib/components/datagrid/Grid.svelte";
    import { getContext, onMount } from "svelte";
    import { patchOfferList, type Offer, fetchOfferList } from "$lib/data/offers";
    import { fetchLogs } from "$lib/data/settings";
    import type { ModalKind } from "$lib/components/modal/Modals.svelte";
    import { ChangeList } from "$lib/components/datagrid/changes";
    import Toolbar from "./Toolbar.svelte";

    let data: Offer[] = [];
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
                await patchOfferList(data.filter(x => changes.isChanged(x.sku)));
                await refreshData();
            }
        });
    }

    /** Refreshes data displayed in the grid. */
    async function refreshData() {
        changes.clear();
        changes = changes;
        data = await fetchOfferList();
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

<main>
    <Toolbar
        on:filterChanged={e => {
            filter = e.detail;
        }}
    />
    <Grid key="sku" bind:data bind:changes bind:filter />
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
