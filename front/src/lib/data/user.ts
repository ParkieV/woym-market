import { fetchJSON, type FetchInit } from "$lib/fetch";
import { type Writable, writable, type Readable, derived, get } from "svelte/store";

export const user: Writable<User | undefined> = writable();
export const userCanModify: Readable<boolean> = derived(user, x => x?.is_staff ?? false);

export async function fetchUser(init?: FetchInit): Promise<User> {
    let { data } = await fetchJSON<User>("/users/me", init);
    return data;
}

export type User = {
    id: number;
    login: string;
    is_staff: boolean;
};
