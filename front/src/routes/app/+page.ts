import { redirect } from "@sveltejs/kit";
import type { PageLoad } from "./$types";

export const load: PageLoad = async () => {
    console.log('Check redirect');
    redirect(303, "/app/offers");
};
