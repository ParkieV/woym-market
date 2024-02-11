import type { OfferBase } from "./offers";

export type FboStocks = OfferBase & {
    storages: FboStorage[];
};

export type FboStorage = {
    id: number;
    current_stock: number;
    min_stock: number;
    warehouse: {
        id: number;
        name: string;
    };
};

export async function fetchFboStocks(): Promise<FboStocks[]> {
    // TODO: replace with API call after backend implementation.
    return [
        {
            sku: "123",
            photo: "https://www.vincenzosplate.com/wp-content/uploads/2023/03/1500x1500-Photo-3_2447-How-to-Make-PECORINO-CHEESE-at-Home-Like-an-Italian-CheeseMaker-V1-1.jpg",
            name: "Товар 1",
            note_1: "",
            note_2: "",
            note_3: "",
            market: "yandex",
            name_of_shop: "MASTERSKRAB",
            hidden: false,
            storages: [
                { id: 0, current_stock: 10, min_stock: 0, warehouse: { id: 0, name: "ABC" } },
                { id: 1, current_stock: 20, min_stock: 0, warehouse: { id: 0, name: "BCD" } },
                { id: 2, current_stock: 30, min_stock: 130, warehouse: { id: 0, name: "SKLAD" } }
            ]
        },
        {
            sku: "456",
            photo: "https://www.vincenzosplate.com/wp-content/uploads/2023/03/1500x1500-Photo-3_2447-How-to-Make-PECORINO-CHEESE-at-Home-Like-an-Italian-CheeseMaker-V1-1.jpg",
            name: "Товар 2",
            note_1: "",
            note_2: "",
            note_3: "",
            market: "yandex",
            name_of_shop: "MASTERSKRAB",
            hidden: false,
            storages: [
                { id: 10, current_stock: 10, min_stock: 50, warehouse: { id: 0, name: "ABC" } }
            ]
        },
        {
            sku: "789",
            photo: "https://www.vincenzosplate.com/wp-content/uploads/2023/03/1500x1500-Photo-3_2447-How-to-Make-PECORINO-CHEESE-at-Home-Like-an-Italian-CheeseMaker-V1-1.jpg",
            name: "Товар 3",
            note_1: "",
            note_2: "",
            note_3: "",
            market: "yandex",
            name_of_shop: "CALMAR.SHOP",
            storages: [],
            hidden: false
        }
    ];
}

export async function patchFboStocks(stocks: FboStocks[]) {
    // TODO: replace with API call after backend implementation.
}
