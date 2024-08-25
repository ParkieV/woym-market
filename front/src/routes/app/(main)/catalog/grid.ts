import { BASE_GRID_OPTIONS } from "$lib/grid/base";
import { GridDefinition } from "$lib/datagrid";
import type { Column, ColumnGroup } from "$lib/datagrid/columns";
import type { CatalogEntry } from "$lib/data/catalog";
import {
    BooleanColumn,
    StringColumn,
    dollarColumn,
    floatColumn,
    GroupColumn,
    ImageColumn,
    DateColumn
} from "$lib/datagrid/columns/types";
import type { Market } from "$lib/data/markets";

export default function catalogGrid(markets: Market[]): GridDefinition<CatalogEntry> {
    return new GridDefinition(BASE_GRID_OPTIONS, columns(markets));
}

function columns(markets: Market[]): (Column | ColumnGroup)[] {
    return [
        {
            base: new GroupColumn(),
            header: "SKU",
            key: "sku",
            pinned: true
        },
        {
            header: "Информация",
            children: [
                {
                    base: new ImageColumn(),
                    header: "Фото",
                    key: "photo"
                },
                {
                    base: new StringColumn(),
                    header: "Название",
                    key: "name",
                    editable: true
                },
                {
                    base: new StringColumn(),
                    key: "barcodes",
                    header: "Штрихкоды",
                    columnGroupShow: "closed",
                    editable: true
                },
                {
                    base: new StringColumn(),
                    header: "Аннотация",
                    key: "description",
                    editable: true,
                    columnGroupShow: "closed"
                },
                {
                    base: new StringColumn(),
                    header: "Примечание",
                    key: "catalog_note",
                    editable: true,
                    columnGroupShow: "closed"
                },
                {
                    base: new StringColumn({
                        kind: "agLargeTextCellEditor",
                        cols: 80,
                        rows: 4,
                        maxLength: 255
                    }),
                    header: "Поисковые слова",
                    key: "search_words",
                    editable: true,
                    columnGroupShow: "closed"
                }
            ]
        },
        {
            header: "Габариты",
            children: [
                { header: "Вес, кг", key: "self_weight", base: floatColumn, editable: true },
                { header: "Длина, см", key: "self_length", base: floatColumn, editable: true },
                { header: "Ширина, см", key: "self_width", base: floatColumn, editable: true },
                { header: "Высота, см", key: "self_height", base: floatColumn, editable: true },
                {
                    key: "self_volume",
                    header: "Объём, л",
                    base: floatColumn,
                    tooltip: "Длина * ширина * высота / 1000"
                }
            ]
        },
        {
            header: "Ценообразование",
            children: [
                {
                    key: "use_promotion_price",
                    header: "Акция",
                    base: new BooleanColumn(),
                    editable: true
                },
                {
                    key: "wholesale_dollar_cost_price",
                    header: "ОПТ у. е.",
                    base: dollarColumn,
                    editable: true
                },
                {
                    key: "dollar_cost_price_updated_at",
                    header: "Дата обновления ОПТ (у. е.)",
                    base: new DateColumn()
                }
            ]
        },
        {
            key: "supplier_available",
            header: "Наличие у поставщика",
            base: new BooleanColumn()
        },
        {
            header: "Синхронизация",
            children: marketColumns(markets)
        }
    ];
}

function marketColumns(markets: Market[]) {
    return markets.map(market => {
        return {
            header: `${market.name} (${market.type})`,
            key: `shops-${market.id}`,
            valueGetter: ({ data }: { data: CatalogEntry }) => {
                let synchronization = data.synchronization.find(
                    ({ market: type, name_of_shop }) =>
                        market.type === type && market.name === name_of_shop
                );
                return synchronization?.synchronization;
            },
            valueSetter: ({ data, newValue }: { data: CatalogEntry; newValue: boolean }) => {
                let synchronization = data.synchronization.find(
                    x => x.market === market.type && x.name_of_shop === market.name
                );
                if (synchronization === undefined) return false;
                synchronization.synchronization = newValue;
                return true;
            },
            base: new BooleanColumn(),
            editable: ({ data }) => {
                if (!data) return false;
                return data.synchronization.some(
                    ({ market: type, name_of_shop }) =>
                        market.type === type && market.name === name_of_shop
                );
            }
        } as Column<CatalogEntry>;
    });
}
