import { goto } from "$app/navigation";
import { PUBLIC_BASE_URL } from "$env/static/public";
import { logout } from "./auth";
import { showLoadingModal, showNotification } from "./components/modal/Modals.svelte";

export const BaseUrl = PUBLIC_BASE_URL;

export async function handleRequest<R extends Response | Response[]>(
    promise: Promise<R>,
    modal?: {
        header?: string;
        errorHeader?: string;
        onSuccess?: (response: Response) => void;
    }
): Promise<R> {
    showLoadingModal(promise, modal?.header ?? "Загрузка...");
    await promise.then(
        async response => {
            let responses = Array.isArray(response) ? response : [response];
            for (const response of responses) {
                if (response.status == 401) {
                    logout();
                    goto("/auth");
                    showNotification(
                        "Ошибка авторизации",
                        "Пожалуйста, повторно войдите в аккаунт."
                    );
                } else if (response.status >= 500 && response.status <= 599) {
                    showNotification("Ошибка сервера", "Не удалось достичь сервера.");
                } else if (response.status >= 400 && response.status <= 499) {
                    showNotification(
                        modal?.errorHeader ?? "Ошибка",
                        (await response.json()).detail
                    );
                } else if (response.ok) {
                    modal?.onSuccess?.(response);
                }
            }
        },
        () => {
            showNotification("Ошибка сети", "Не удалось достичь сервера.");
        }
    );
    return promise;
}
