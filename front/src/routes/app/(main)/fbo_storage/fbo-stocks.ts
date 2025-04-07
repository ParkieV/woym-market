import type { FboStocks } from "$lib/data/fbo_storage";
import { GridDefinition } from "$lib/datagrid";
import type { Column, ColumnGroup } from "$lib/datagrid/columns";
import {
    BooleanColumn,
    DateColumn,
    intColumn,
    NumberColumn,
    StringColumn
} from "$lib/datagrid/columns/types";
import { BASE_GRID_OPTIONS } from "$lib/grid/base";
import type { GridOptions } from "ag-grid-enterprise";
import { fboStocksSelection } from "../selection";
import { get } from "svelte/store";

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
            base: {
                cellRenderer: ({ data, value }) => {
                    const url = "/graph.svg";
                    const style = "height: 16px; margin: 0 1px -3px 0;";
                    const img = `<img style=\"${style}\" src=\"${url}\" />`;
                    if (data.warehouse.warehouse_type === "cluster") return `${img} ${value}`;
                    else if (data.warehouse.warehouse_type === "super_cluster") return `${img} ${value.substring(1)}`;
                    else return `${value}`;
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
        }
    ];
}

export function calcToDeliver({
    min_stock,
    current_stock,
    is_deliver_in_boxes,
    in_box
}: FboStocks): number {
    let diff = Math.max(0, Math.abs(min_stock - current_stock));
    if (is_deliver_in_boxes) {
        let boxes_remainder = 0;
        if (diff % in_box !== 0) boxes_remainder = 1;
        let boxes = Math.floor(diff / in_box) + boxes_remainder;
        return boxes * in_box;
    }
    return diff;
}

export function getSelectedStocks(market: string) {
    const selectedMap = get(fboStocksSelection.selected);
    const selectedRows = Array.from(selectedMap.values());
    return selectedRows
        .filter(x => x.warehouse.market === market)
        .map(row => ({
        id: row.id,
        warehouse_name: row.warehouse.name,
        to_deliver_number: calcToDeliver(row)
    }));
}