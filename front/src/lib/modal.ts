import { openModal } from "svelte-modals";
import ConfirmationDialog from "$lib/components/modal/ConfirmationDialog.svelte";
import FetchDialog from "$lib/components/modal/FetchDialog.svelte";

export async function showFetchModals<R extends Response | Response[]>(
    promise: Promise<R>,
    loadingHeader?: string,
    errorHeader?: string
) {
    openModal(FetchDialog, { header: loadingHeader ?? "Загрузка...", promise });

    promise.then(
        async response => {
            let responses: Response[] = Array.isArray(response) ? response : [response];
            for (const response of responses) handleResponse(response);
        },
        _ => {
            showNotification("Ошибка сети", "Не удалось достичь сервера.");
        }
    );

    async function handleResponse(response: Response) {
        if (response.status == 401) {
            showNotification("Ошибка авторизации", "Пожалуйста, повторно войдите в аккаунт.");
        } else if (response.status >= 500 && response.status <= 599) {
            showNotification("Ошибка сервера", "Не удалось достичь сервера.");
        } else if (response.status >= 400 && response.status <= 499) {
            showNotification(errorHeader ?? "Ошибка", printError((await response.json()).detail));
        }

        function printError(detail: unknown): string {
            if (detail === undefined || detail === null) return "";
            if (typeof detail === "string") return detail.toString();
            console.error(detail);
            return "Неожиданная ошибка";
        }
    }
}

export function showNotification(header: string, text: string) {
    openModal(ConfirmationDialog, { header, text, showCancelButton: false });
}
