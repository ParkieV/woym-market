<script lang="ts" context="module">
    export type ModalKind =
        | { kind: "confirmChangesLoss"; changed: number; onConfirm: () => void }
        | { kind: "confirmSave"; onConfirm: () => void }
        | { kind: "dataUpdatedOnServer" }
        | {
              kind: "await";
              promise: Promise<any>;
              header: string;
              errorHeader: string;
              errorText: string;
          };
</script>

<script lang="ts">
    import FetchDialog from "$lib/modal/FetchDialog.svelte";
    import ConfirmationDialog from "$lib/modal/ConfirmationDialog.svelte";
    import NotificationDialog from "$lib/modal/NotificationDialog.svelte";
    import { num_word } from "$lib/util";

    export let modals: ModalKind[];
    $: modal = modals.at(-1);

    let close = () => {
        modals.pop();
        modals = modals;
    };
</script>

{#if modal}
    {#if modal.kind == "confirmChangesLoss"}
        {@const word = num_word(modal.changed, ["изменение", "изменения", "изменений"])}
        {@const part = num_word(modal.changed, [
            "Оно будет потеряно",
            "Они будут потеряны",
            "Они будут потеряны"
        ])}
        <ConfirmationDialog
            header="Изменения будут потеряны"
            text={`Вы внесли ${modal.changed} ${word}. ${part}, продолжить?`}
            on:confirm={modal.onConfirm}
            on:close={close}
        />
    {:else if modal.kind == "confirmSave"}
        <ConfirmationDialog
            header="Сохранить изменения?"
            text="Данные обновятся на сервере"
            on:confirm={modal.onConfirm}
            on:close={close}
        />
    {:else if modal.kind == "dataUpdatedOnServer"}
        <NotificationDialog
            header="Информация устарела"
            text="Данные в таблице были обновлены"
            on:close={close}
        />
    {:else if modal.kind == "await"}
        {@const { header, promise, errorHeader, errorText } = modal}
        <FetchDialog {header} {promise} {errorHeader} {errorText} on:close={close} />
    {/if}
{/if}
