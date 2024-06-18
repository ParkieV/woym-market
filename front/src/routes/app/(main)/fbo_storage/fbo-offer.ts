import type { Column, ColumnGroup } from "$lib/datagrid/columns";
import type { GetContextMenuItems, ValueGetterParams } from "ag-grid-enterprise";
import type { FboStocks, FboStorage } from "$lib/data/fbo_storage";
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
import { get, type Writable } from "svelte/store";
import { userCanModify } from "$lib/data/user";
import type { ChangeList } from "$lib/datagrid/plugins/changes";
import { selectedContextMenuItems } from "./selected";
import { calcToDeliver } from "./fbo-warehouse";

export default function fboOffersGrid(
    changes: Writable<ChangeList<FboStocks, "id">>,
    innerChanges: Writable<ChangeList<FboStorage, "id">>
): GridDefinition<FboStocks> {
    return new GridDefinition({ ...BASE_GRID_OPTIONS, getContextMenuItems }, columns());

    function getContextMenuItems(): ReturnType<GetContextMenuItems<FboStocks>> {
        if (!get(userCanModify)) {
            return ["copy"];
        } else {
            return [
                "cut",
                "copy",
                "paste",
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
                    valueGetter: e => e.data.self_weight * e.getValue("to_deliver")
                },
                {
                    base: floatColumn,
                    key: "volume",
                    header: "Объём, л",
                    valueGetter: e => e.data.volume * e.getValue("to_deliver")
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
                    valueGetter: (params: ValueGetterParams<FboStocks>) => {
                        if (!params.data) return 0;
                        return params.data.stocks
                            .map(x => x.current_stock)
                            .reduce((a, b) => a + b, 0);
                    }
                },
                {
                    header: "Мин. остаток",
                    key: "min_stock",
                    base: intColumn,
                    valueGetter: (params: ValueGetterParams<FboStocks>) => {
                        if (!params.data) return 0;
                        return params.data.stocks.map(x => x.min_stock).reduce((a, b) => a + b, 0);
                    }
                },
                {
                    header: "К поставке",
                    key: "to_deliver",
                    base: intColumn,
                    valueGetter: (params: ValueGetterParams<FboStocks>) => {
                        if (!params.data) return 0;
                        return params.data.stocks.reduce(
                            (sum, storage) => sum + calcToDeliver(storage),
                            0
                        );
                    }
                },
                {
                    key: "supplier_available",
                    header: "Наличие у поставщика",
                    base: new BooleanColumn()
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

export function calcStocksToDeliver(stock: FboStocks) {
    return stock.stocks.reduce((sum, storage) => sum + calcToDeliver(storage), 0);
}
