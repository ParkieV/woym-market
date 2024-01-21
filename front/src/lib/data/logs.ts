import { fetchAuthenticated } from "$lib/auth";

export type Logs = {
    updated_at: string | null;
};

export async function fetchLogs(): Promise<Logs> {
    return await (await fetchAuthenticated("offers/logs")).json();
}
