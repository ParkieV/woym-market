import type { Column, ColumnGroup } from "$lib/components/datagrid/columns";
import type { Market } from "$lib/data/markets";
import type { OwnStorage } from "$lib/data/own_storage";
import {
    GroupColumn,
    StringColumn,
    ImageColumn,
    intColumn
} from "$lib/components/datagrid/columns/types";

export default function ownStorageColumns(markets: Market[]): (Column | ColumnGroup)[] {
    const noteCols = ([1, 2, 3] as const).map(i => {
        return {
            header: `Примечание ${i}`,
            key: `note_${i}`,
            valueGetter: ({ data }: { data: OwnStorage }) =>
                data[`note_${i}`].filter(x => x !== "").join("; "),
            base: new StringColumn(),
            columnGroupShow: "closed"
        } as Column;
    });
    const marketCols = markets.map(market => {
        return {
            header: `${market.name} (${market.type}), шт.`,
            key: `shops-${market.id}`,
            valueGetter: ({ data }: { data: OwnStorage }) => {
                let stock = data.stocks.find(
                    ({ market: type, name_of_shop }) =>
                        market.type === type && market.name === name_of_shop
                );
                return stock?.value;
            },
            base: intColumn
        } as Column;
    });

    return [
        {
            header: "SKU",
            key: "sku",
            base: new GroupColumn(),
            pinned: true
        },
        {
            header: "Информация",
            children: [
                {
                    header: "Фото",
                    key: "photo",
                    base: new ImageColumn(),
                    valueGetter: ({ data }: { data: OwnStorage }) => {
                        if (data.photo === undefined || data.photo.length === 0) return null;
                        let photo = data.photo
                            .map(x => x ?? "")
                            .filter(x => x !== "")
                            .at(0);
                        return photo ?? null;
                    }
                },
                { header: "Название", key: "name.0", base: new StringColumn() },
                ...noteCols
            ]
        },
        {
            header: "Мой склад",
            key: "own_storage.value",
            base: intColumn,
            editable: true
        },
        ...marketCols
    ];
}
