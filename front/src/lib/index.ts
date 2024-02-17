import { goto } from "$app/navigation";
import { PUBLIC_BASE_URL } from "$env/static/public";
import { logout } from "./auth";
import { showLoadingModal, showNotification } from "./components/modal/Modals.svelte";

export const BaseUrl = PUBLIC_BASE_URL;

export async function handleRequest<T, R extends Response | Response[]>(
    promise: Promise<R>,
    modal?: Partial<ModalSettings<T, R>>
): Promise<T | undefined> {
    let _modal = normalizeModal(modal ?? {});
    showLoadingModal(promise, _modal.header);
    return new Promise((resolve, reject) => {
        promise.then(
            async response => {
                let responses: Response[] = Array.isArray(response) ? response : [response];
                for (const response of responses) {
                    if (response.ok) continue;
                    if (response.status == 401) {
                        logout();
                        await goto("/auth");
                        showNotification(
                            "Ошибка авторизации",
                            "Пожалуйста, повторно войдите в аккаунт."
                        );
                    } else if (response.status >= 500 && response.status <= 599) {
                        showNotification("Ошибка сервера", "Не удалось достичь сервера.");
                    } else if (response.status >= 400 && response.status <= 499) {
                        showNotification(_modal.errorHeader, (await response.json()).detail);
                    }
                    reject();
                    return;
                }
                resolve(_modal.onSuccess?.(response));
            },
            () => {
                showNotification("Ошибка сети", "Не удалось достичь сервера.");
                reject();
            }
        );
    });
}

/** Sets default values for modal settings. */
function normalizeModal<T, R extends Response | Response[]>(
    partial: Partial<ModalSettings<T, R>>
): ModalSettings<T, R> {
    return {
        header: partial.header ?? "Загрузка...",
        errorHeader: partial.errorHeader ?? "Ошибка",
        onSuccess: partial.onSuccess
    };
}

type ModalSettings<T, R extends Response | Response[]> = {
    header: string;
    errorHeader: string;
    onSuccess?: (response: R) => T;
};
