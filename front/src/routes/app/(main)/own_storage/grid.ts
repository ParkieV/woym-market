import type { Column, ColumnGroup } from "$lib/datagrid/columns";
import type { Market } from "$lib/data/markets";
import type { OwnStorage } from "$lib/data/own_storage";
import { GroupColumn, StringColumn, ImageColumn, intColumn } from "$lib/datagrid/columns/types";
import { GridDefinition } from "$lib/datagrid";
import { BASE_GRID_OPTIONS } from "$lib/grid/base";
import type { StoragePlace } from "$lib/data/own_storage/places";

export default function ownStorageGrid(
    markets: Market[],
    storages: StoragePlace[]
): GridDefinition {
    return new GridDefinition(BASE_GRID_OPTIONS, columns(markets, storages));
}

function columns(markets: Market[], storages: StoragePlace[]): (Column | ColumnGroup)[] {
    return [
        {
            header: "SKU",
            key: "offer.sku",
            base: new GroupColumn(),
            pinned: true
        },
        {
            header: "Информация",
            children: [
                {
                    header: "Фото",
                    key: "offer.photo",
                    base: new ImageColumn(),
                    valueGetter: ({ data }: { data: OwnStorage }) =>
                        data.offer.photo.filter(x => x !== null).at(0)
                },
                {
                    header: "Название",
                    key: "offer.name",
                    base: new StringColumn(),
                    valueGetter: ({ data }: { data: OwnStorage }) =>
                        data.offer.name.filter(x => x !== null).at(0)
                },
                {
                    header: "Примечание 1",
                    key: "offer.note_1",
                    base: new StringColumn(),
                    valueGetter: ({ data }: { data: OwnStorage }) =>
                        joinNullableStringArray(data.offer.note_1),
                    columnGroupShow: "open"
                },
                {
                    header: "Примечание 2",
                    key: "offer.note_2",
                    base: new StringColumn(),
                    valueGetter: ({ data }: { data: OwnStorage }) =>
                        joinNullableStringArray(data.offer.note_2),
                    columnGroupShow: "open"
                },
                {
                    header: "Примечание 3",
                    key: "offer.note_3",
                    base: new StringColumn(),
                    valueGetter: ({ data }: { data: OwnStorage }) =>
                        joinNullableStringArray(data.offer.note_3),
                    columnGroupShow: "open"
                },
                {
                    header: "Штрихкоды",
                    key: "barcodes",
                    base: new StringColumn(),
                    valueGetter: ({ data }: { data: OwnStorage }) =>
                        joinNullableStringArray(data.offer.barcodes),
                    columnGroupShow: "open"
                }
            ]
        },
        {
            header: "Склады",
            children: storageColumns(storages)
        },
        {
            header: "Магазины",
            children: marketColumns(markets)
        }
    ];
}

function marketColumns(markets: Market[]) {
    return markets.map(market => {
        return {
            header: `${market.name} (${market.type}), шт.`,
            key: `shops-${market.id}`,
            valueGetter: ({ data }: { data: OwnStorage }) => {
                let stock = data.stocks.find(
                    ({ market: type, name_of_shop }) =>
                        market.type === type && market.name === name_of_shop
                );
                return stock?.stock;
            },
            base: intColumn
        } as Column;
    });
}

function storageColumns(storages: StoragePlace[]) {
    return storages.map(storage => {
        return {
            header: `${storage.name}, шт.`,
            key: `shops-${storage.id}`,
            valueGetter: ({ data }: { data: OwnStorage }) => {
                let stock = data.storages.find(
                    ({ storage_place_id }) => storage_place_id === storage.id
                );
                return stock?.value;
            },
            editable: true,
            base: intColumn
        } as Column;
    });
}

function joinNullableStringArray(data: (string | null)[]): string | null {
    if (data.every(x => x === null)) return null;
    return data.filter(x => x !== null && x !== "").join();
}
