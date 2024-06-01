import type { Column, ColumnGroup } from "$lib/components/datagrid/columns";
import { StringColumn, intColumn } from "$lib/components/datagrid/columns/types";

export default function fboWarehouseColumns(): (Column | ColumnGroup)[] {
    return [
        { header: "Склад", key: "warehouse.name", base: new StringColumn() },
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
                    return Math.max(0, params.data.min_stock - params.data.current_stock);
                } else {
                    return 0;
                }
            }
        }
    ];
}
