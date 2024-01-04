export const BaseUrl = "http://5.35.88.225:8000/";

export async function patchUserInfo(val: { rate: number }): Promise<void> {
    let init: RequestInit = {
        method: "PATCH",
        body: JSON.stringify(val),
        headers: {
            "Content-Type": "application/json"
        }
    };
    await fetchAuthenticated("users/settings", init);
}

export async function fetchUserInfo(): Promise<{ rate: number }> {
    let info = await (await fetchAuthenticated("users/settings")).json();
    return info;
}
