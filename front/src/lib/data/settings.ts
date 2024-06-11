import { fetchJSON } from "$lib/fetch";

export type Logs = {
    updated_at: string | null;
};

export async function fetchLogs(): Promise<Logs> {
    return fetchJSON<Logs>("settings/logs").then(x => x.data);
}
