import type { FboStocks } from "$lib/data/fbo_stocks";
import { GridDefinition } from "$lib/datagrid";
import type { Column, ColumnGroup } from "$lib/datagrid/columns";
import {
    BooleanColumn,
    DateColumn,
    NumberColumn,
    StringColumn,
    floatColumn,
    intColumn
} from "$lib/datagrid/columns/types";
import { BASE_GRID_OPTIONS } from "$lib/grid/base";
import type { GridOptions } from "ag-grid-enterprise";

export default function fboStocks(): GridDefinition<FboStocks> {
    const options: GridOptions = {
        ...BASE_GRID_OPTIONS,
        rowHeight: 30,
        autoSizeStrategy: { type: "fitCellContents" },
        suppressMovableColumns: true
    };
    const definition = new GridDefinition(options, columns());
    return definition;
}

function columns(): (Column | ColumnGroup)[] {
    return [
        {
            header: "Склад",
            key: "warehouse.name",
            pinned: true,
            valueGetter: ({ data }: { data: FboStocks }) => {
                // TODO: no warehouse id
                return { warehouse_type: "super_warehouse", name: "Test" };
            },
            base: {
                cellRenderer: ({ value }) => {
                    if (value.warehouse_type === "warehouse") return value.name;
                    const url = value.warehouse_type === "cluster" ? "/graph.svg" : "/globe.svg";
                    const style = "height: 16px; margin: 0 1px -3px 0;";
                    const img = `<img style=\"${style}\" src=\"${url}\" />`;
                    return `${img} ${value.name}`;
                }
            }
        },
        {
            header: "В наличии",
            key: "current_stock",
            base: intColumn
        },
        {
            header: "Мин. остаток",
            key: "min_stock",
            base: intColumn,
            editable: true
        },
        {
            header: "К поставке",
            key: "to_deliver",
            base: intColumn,
            valueGetter: params => {
                if (params.data) {
                    return calcToDeliver(params.data);
                } else {
                    return 0;
                }
            }
        },
        {
            key: "from_file_updated_at",
            header: "Дата последней загрузки",
            base: new DateColumn()
        },
        {
            key: "can_be_delivered",
            header: "Возможна ли поставка",
            base: new BooleanColumn()
        },
        {
            key: "advice_from_the_store",
            header: "Совет",
            base: new StringColumn()
        },
        {
            key: "in_box",
            header: "В коробке",
            base: new NumberColumn({ precision: 0, min: 1 }),
            editable: true
        },
        {
            key: "is_deliver_in_boxes",
            header: "Поставлять коробками",
            base: new BooleanColumn(),
            editable: true
        },
        {
            header: "Статистика",
            children: [
                { key: "statistics.today", header: "Сегодня", base: floatColumn },
                { key: "statistics.yesterday", header: "Вчера", base: floatColumn },
                { key: "statistics.for_7_days", header: "7 дней", base: floatColumn },
                { key: "statistics.for_14_days", header: "14 дней", base: floatColumn },
                { key: "statistics.for_28_days", header: "28 дней", base: floatColumn },
                { key: "statistics.for_60_days", header: "60 дней", base: floatColumn },
                { key: "statistics.for_120_days", header: "120 дней", base: floatColumn },
                { key: "statistics.smart_delivery", header: "Умная поставка", base: floatColumn },
                {
                    key: "statistics.use_smart_delivery",
                    header: "Использовать умную поставку",
                    base: new BooleanColumn()
                }
            ]
        }
    ];
}

export function calcToDeliver({
    min_stock,
    current_stock,
    is_deliver_in_boxes,
    in_box
}: FboStocks): number {
    let diff = Math.max(0, min_stock - current_stock);
    if (is_deliver_in_boxes) {
        let boxes_remainder = 0;
        if (diff % in_box !== 0) boxes_remainder = 1;
        let boxes = Math.floor(diff / in_box) + boxes_remainder;
        return boxes * in_box;
    }
    return diff;
}
