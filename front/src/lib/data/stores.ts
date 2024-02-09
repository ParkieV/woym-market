export type Store = {
    id: number;
    name: string;
};

export async function getStores(): Promise<Store[]> {
    // TODO: replace with API call after backend implementation.
    return [
        { id: 0, name: "CALMAR.SHOP" },
        { id: 1, name: "MASTERSKRAB" }
    ];
}
