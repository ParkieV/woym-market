import type { Column, ColumnGroup } from "$lib/datagrid/columns";
import type { GetContextMenuItems, ValueGetterParams } from "ag-grid-enterprise";
import type { FboStorage, FboStocks } from "$lib/data/fbo_storage";
import {
    BooleanColumn,
    GroupColumn,
    ImageColumn,
    StringColumn,
    floatColumn,
    intColumn,
    percentColumn,
    rubleColumn
} from "$lib/datagrid/columns/types";
import { BASE_GRID_OPTIONS } from "$lib/grid/base";
import { GridDefinition } from "$lib/datagrid";
import { get } from "svelte/store";
import { userCanModify } from "$lib/data/user";
import type { ChangeList } from "$lib/datagrid/plugins/changes";
import { selectedContextMenuItems } from "./selected";
import { calcToDeliver, getSelectedStocks } from "./fbo-stocks";
import { fboStorageSelection } from "../selection";

export default function fboOffersGrid(
    changes: ChangeList<FboStorage, number>,
    innerChanges: ChangeList<FboStocks, number>
): GridDefinition<FboStorage> {
    return new GridDefinition({ ...BASE_GRID_OPTIONS, getContextMenuItems }, columns());

    function getContextMenuItems(): ReturnType<GetContextMenuItems<FboStorage>> {
        if (!get(userCanModify)) {
            return ["copy", "resetColumns"];
        } else {
            return [
                "cut",
                "copy",
                "paste",
                "resetColumns",
                "separator",
                ...selectedContextMenuItems(changes, innerChanges)
            ];
        }
    }
}

function columns(): (Column | ColumnGroup)[] {
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
                    key: "name"
                },
                {
                    base: new StringColumn(),
                    header: "Примечание 1",
                    key: "note_1",
                    editable: true,
                    columnGroupShow: "closed"
                },
                {
                    base: new StringColumn(),
                    header: "Примечание 2",
                    key: "note_2",
                    editable: true,
                    columnGroupShow: "closed"
                },
                {
                    base: new StringColumn(),
                    header: "Примечание 3",
                    key: "note_3",
                    editable: true,
                    columnGroupShow: "closed"
                },
                {
                    base: new StringColumn(),
                    key: "barcodes",
                    header: "Штрихкоды",
                    columnGroupShow: "closed"
                },
                {
                    base: new StringColumn(),
                    key: "market",
                    header: "Площадка",
                    columnGroupShow: "closed"
                },
                {
                    base: new StringColumn(),
                    key: "name_of_shop",
                    header: "Название магазина",
                    columnGroupShow: "closed"
                },
                {
                    base: floatColumn,
                    key: "self_weight",
                    header: "Вес, кг",
                    valueGetter: (e: ValueGetterParams<FboStorage>) => (e.data?.self_weight || 0) * e.getValue("to_deliver")
                },
                {
                    base: floatColumn,
                    key: "volume",
                    header: "Объём, л",
                    valueGetter: (e: ValueGetterParams<FboStorage>) => (e.data?.volume || 0) * e.getValue("to_deliver")
                }
            ]
        },
        {
            header: "Остатки",
            children: [
                {
                    header: "В наличии",
                    key: "current_stock",
                    base: intColumn,
                    valueGetter: (params: ValueGetterParams<FboStorage>) => {
                        if (!params.data) return 0;
                        const stocks = params.data.stocks
                            .filter(x => x.warehouse.warehouse_type === "warehouse")
                            .map(x => x.current_stock)
                            .reduce((a, b) => a + b, 0);
                        return stocks / 2;
                    }
                },
                {
                    header: "Мин. остаток",
                    key: "min_stock",
                    base: intColumn,
                    valueGetter: (params: ValueGetterParams<FboStorage>) => {
                        if (!params.data) return 0;
                        return params.data.stocks
                            .filter(x => x.warehouse.warehouse_type === "warehouse")
                            .map(x => x.min_stock)
                            .reduce((a, b) => a + b, 0);
                    }
                },
                {
                    header: "К поставке",
                    key: "to_deliver",
                    base: intColumn,
                    valueGetter: (params: ValueGetterParams<FboStorage>) => {
                        if (!params.data) return 0;
                        return params.data.stocks
                            .filter(x => x.warehouse.warehouse_type === "warehouse")
                            .reduce((sum, storage) => sum + calcToDeliver(storage), 0);
                    }
                },
                {
                    key: "supplier_available",
                    header: "Наличие у поставщика",
                    base: new BooleanColumn(),
                    editable: true
                }
            ]
        },
        {
            header: "Ценообразование",
            children: [
                {
                    key: "cost_price",
                    header: "Стоимость",
                    base: rubleColumn,
                    valueGetter: e => e.data.cost_price * e.getValue("to_deliver")
                },
                {
                    key: "margin",
                    header: "Окупаемость",
                    base: percentColumn
                },
                {
                    key: "profit",
                    header: "Предполагаемая прибыль",
                    base: floatColumn,
                    valueGetter: e => e.data.profit * e.getValue("to_deliver")
                }
            ]
        },
        { header: "Скрыт", key: "hidden", base: new BooleanColumn(), editable: true }
    ];
}

export function calcStocksToDeliver(stock: FboStorage) {
    return stock.stocks.reduce((sum, storage) => sum + calcToDeliver(storage), 0);
}

export function getSelectedOrders() {
    const selectedMap = get(fboStorageSelection.selected); // Получаем выделенные строки в виде Map
    const selectedRows = Array.from(selectedMap.values()); // Преобразуем в массив значений
    console.log("selected rows:", selectedRows);
    const orders = selectedRows.map(row => ({
        sku: row.sku,
        marketplace_name: row.market,
        shop_name: row.name_of_shop,
        weight: row.self_weight !== null? row.self_weight : 0,
        volume: row.volume !== null? row.volume : 0,
        cost_price: row.cost_price !== null? row.cost_price : 0,
        goods_name: row.name,
        to_deliver_number: row.stocks
            .filter(x => x.warehouse.warehouse_type === "warehouse")
            .reduce((sum, storage) => sum + calcToDeliver(storage), 0),
        warehouses: getSelectedStocks(row.market)
    }));
    console.log("request orders", orders);
    return orders;
}