<script lang="ts" generics="T, K extends keyof T">
    import {
        showChangesLossConfirmation,
        showSaveConfirmation,
        showNotification
    } from "$lib/components/modal/Modals.svelte";
    import { fetchLogs } from "$lib/data/settings";
    import type { ChangeList } from "$lib/components/datagrid/changes";
    import { createEventDispatcher, getContext, onMount } from "svelte";

    export let changes: ChangeList<T, K>;
    let updated_at: Date | null = null;

    const dispatch = createEventDispatcher<{ save: void; reload: void }>();

    onMount(() => {
        const fetchDate = async () => {
            let logs = await fetchLogs();
            if (!logs.updated_at) return;
            let new_updated_at = new Date(logs.updated_at);

            if (updated_at === null) {
                updated_at = new_updated_at;
            } else if (updated_at < new_updated_at) {
                updated_at = new_updated_at;
                showNotification("Информация устарела", "Данные на сервере были обновлены.");
                dispatch("reload");
            }
        };
        fetchDate();
        setInterval(fetchDate, 15 * 1000);
    });

    async function cancelEdits() {
        if (changes.hasChanges) {
            showChangesLossConfirmation(changes.count, () => dispatch("reload"));
        } else {
            dispatch("reload");
        }
    }

    async function confirmSave() {
        showSaveConfirmation(() => {
            dispatch("save");
        });
    }
</script>

<footer>
    <span
        >{`Последнее обновление:\n${updated_at ? updated_at.toLocaleString("en-GB") : "N/A"}`}</span
    >
    <div style:flex="1" />
    <button class="cancel" on:click={cancelEdits} disabled={!changes.hasChanges}> Отмена </button>
    <button class="confirm" on:click={confirmSave} disabled={!changes.hasChanges}>
        Сохранить
    </button>
</footer>

<style lang="scss">
    @use "mixins" as *;

    footer {
        display: flex;
        align-items: center;
        padding: 16px;
        gap: 16px;
        background-color: #ebebeb;
        margin-top: auto;
        button {
            padding-left: 16px;
            padding-right: 16px;
            &.confirm {
                @include primary-button;
                height: 40px;
            }
            &.cancel {
                @include secondary-button;
                height: 40px;
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
