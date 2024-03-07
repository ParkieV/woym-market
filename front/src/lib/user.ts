import { type Writable, writable, type Readable, derived } from "svelte/store";
import { fetchAuthenticated } from "./auth";

export const user: Writable<User | undefined> = writable();
export const userCanModify: Readable<boolean> = derived(user, x => x?.is_staff ?? false);

export async function fetchUser() {
    try {
        let response = await fetchAuthenticated("users/me");
        let data: User = await response.json();
        user.set(data);
    } catch {}
}

export type User = {
    id: number;
    login: string;
    is_staff: boolean;
};
