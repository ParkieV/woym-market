import { browser } from "$app/environment";
import { showNotification } from "$lib/components/modal/Modals.svelte";
import { fetchJSON } from "$lib/fetch";
import { derived, writable, type Readable, type Writable } from "svelte/store";

export const localUpdatedAt: Writable<Date | null> = writable(null);
export const serverUpdatedAt: Writable<Date | null> = writable(null);

export const shouldReload: Readable<boolean> = derived(
    [localUpdatedAt, serverUpdatedAt],
    ([localUpdatedAt, serverUpdatedAt]) => {
        if (serverUpdatedAt === null) {
            return false;
        } else if (localUpdatedAt === null) {
            return true;
        } else if (localUpdatedAt < serverUpdatedAt) {
            showNotification("Информация устарела", "Данные на сервере были обновлены.");
            return true;
        } else {
            return false;
        }
    }
);

/** Sets local update time to current time. */
export function setLocalUpdateTime() {
    localUpdatedAt.set(new Date());
}

async function setServerUpdateTime() {
    const updatedAt = (await fetchLogs()).updated_at;
    if (!updatedAt) return;
    serverUpdatedAt.set(new Date(updatedAt));
    const dateStr: string = serverUpdatedAt.toLocaleString();
}

if (browser) {
    const time = 15 * 1000;
    setInterval(setServerUpdateTime, time);
    setInterval(setLocalUpdateTime, time);
    setServerUpdateTime();
}

async function fetchLogs(): Promise<Logs> {
    const res = fetchJSON<Logs>("/settings/logs").then(x => x.data);
    return res;
}

type Logs = {
    updated_at: string | null;
};
