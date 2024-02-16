<script lang="ts" context="module">
    import { openModal } from "svelte-modals";

    export function showChangesLossConfirmation(changed: number, onConfirm?: () => void) {
        const word = num_word(changed, ["изменение", "изменения", "изменений"]);
        const part = num_word(changed, [
            "Оно будет потеряно",
            "Они будут потеряны",
            "Они будут потеряны"
        ]);
        const header = "Изменения будут потеряны";
        const text = `Вы внесли ${changed} ${word}. ${part}. Продолжить?`;
        openModal(ConfirmationDialog, { header, text, onConfirm, showCancelButton: true });
    }

    export function showSaveConfirmation(onConfirm?: () => void) {
        const header = "Сохранить изменения?";
        const text = "Данные обновятся на сервере";
        openModal(ConfirmationDialog, { header, text, onConfirm, showCancelButton: true });
    }

    export function showNotification(header: string, text: string) {
        openModal(ConfirmationDialog, { header, text, showCancelButton: false });
    }

    export function showLoadingModal<T>(promise: Promise<T>, header?: string) {
        openModal(FetchDialog<T>, { header: header ?? "Загрузка...", promise });
    }
</script>

<script lang="ts">
    import { Modals } from "svelte-modals";
    import ConfirmationDialog from "$lib/components/modal/ConfirmationDialog.svelte";
    import { num_word } from "$lib/util";
    import FetchDialog from "./FetchDialog.svelte";
</script>

<Modals />
