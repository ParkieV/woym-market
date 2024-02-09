export type Storage = {
    sku: string;
    photo: string;
    name: string;
    note_1: string;
    note_2: string;
    note_3: string;
    own_storage: number;
    shops: Record<number, number | null>;
    hidden: boolean;
};

export async function fetchStorages(): Promise<Storage[]> {
    // TODO: replace with API call after backend implementation.
    return [
        {
            sku: "123",
            photo: "https://www.vincenzosplate.com/wp-content/uploads/2023/03/1500x1500-Photo-3_2447-How-to-Make-PECORINO-CHEESE-at-Home-Like-an-Italian-CheeseMaker-V1-1.jpg",
            name: "Товар 1",
            note_1: "",
            note_2: "",
            note_3: "",
            own_storage: 123,
            shops: {
                "0": 4192,
                "1": 12
            },
            hidden: false
        },
        {
            sku: "456",
            photo: "https://www.vincenzosplate.com/wp-content/uploads/2023/03/1500x1500-Photo-3_2447-How-to-Make-PECORINO-CHEESE-at-Home-Like-an-Italian-CheeseMaker-V1-1.jpg",
            name: "Товар 2",
            note_1: "",
            note_2: "",
            note_3: "",
            own_storage: 100,
            shops: {
                "0": 5,
                "1": null
            },
            hidden: false
        }
    ];
}

export async function patchStorages(storages: Storage[]) {
    // TODO: replace with API call after backend implementation.
}
