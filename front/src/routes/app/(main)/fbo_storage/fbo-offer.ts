import type { Column, ColumnGroup } from "$lib/datagrid/columns";
import type {
    GetContextMenuItems,
    GetContextMenuItemsParams,
    ValueGetterParams
} from "ag-grid-enterprise";
import type { FboStocks, FboStorage } from "$lib/data/fbo_storage";
import {
    BooleanColumn,
    GroupColumn,
    ImageColumn,
    StringColumn,
    floatColumn,
    intColumn
} from "$lib/datagrid/columns/types";
import { BASE_GRID_OPTIONS } from "$lib/grid/base";
import { GridDefinition } from "$lib/datagrid";
import { get } from "svelte/store";
import { userCanModify } from "$lib/data/user";
import type { ChangeList } from "$lib/datagrid/plugins/changes";
import { selectedContextMenuItems, selectedStocks, selectedStorage } from "./selected";

export default function fboOffersGrid(
    changes: ChangeList<FboStocks, "id">,
    innerChanges: ChangeList<FboStorage, "id">
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
                    key: "total_weight",
                    header: "Вес, кг",
                    base: floatColumn
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
                        return params.data.stocks
                            .map(x => Math.max(0, x.min_stock - x.current_stock))
                            .reduce((a, b) => a + b, 0);
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
                    key: "total_cost_price",
                    header: "Стоимость",
                    base: floatColumn
                },
                {
                    key: "total_margin",
                    header: "Окупаемость",
                    base: floatColumn
                },
                {
                    key: "total_profit",
                    header: "Предполагаемая прибыль",
                    base: floatColumn
                }
            ]
        },
        { header: "Скрыт", key: "hidden", base: new BooleanColumn(), editable: true }
    ];
}
