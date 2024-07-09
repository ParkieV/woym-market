<script lang="ts" generics="T, K extends keyof T">
    import { serverUpdatedAt } from "$lib/data/settings";

    import {
        showChangesLossConfirmation,
        showSaveConfirmation
    } from "$lib/components/modal/Modals.svelte";
    import type { ChangeList } from "$lib/datagrid/plugins/changes";
    import { createEventDispatcher } from "svelte";
    import { userCanModify } from "$lib/data/user";

    export let changes: ChangeList<T, K>;

    const dispatch = createEventDispatcher<{ save: void; cancel: void }>();

    async function cancelEdits() {
        if ($changes.hasChanges) {
            showChangesLossConfirmation($changes.count, () => dispatch("cancel"));
        } else {
            dispatch("cancel");
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
        >{`Последнее обновление:\n${
            $serverUpdatedAt ? $serverUpdatedAt.toLocaleString("en-GB") : "N/A"
        }`}</span
    >
    <div style:flex="1" />
    {#if $userCanModify}
        <button class="cancel" on:click={cancelEdits} disabled={!$changes.hasChanges}>
            Отмена
        </button>
        <button class="confirm" on:click={confirmSave} disabled={!$changes.hasChanges}>
            Сохранить
        </button>
    {/if}
</footer>

<style lang="scss">
    @use "mixins" as *;

    footer {
        display: flex;
        align-items: center;
        height: 70px;
        padding: 0 16px;
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
        }
        > span {
            font-size: 16px;
            white-space: pre-wrap;
        }
    }
</style>
