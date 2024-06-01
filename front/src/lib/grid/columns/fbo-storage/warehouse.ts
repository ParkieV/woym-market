import type { Column, ColumnGroup } from "$lib/components/datagrid/columns";
import {
    BooleanColumn,
    DateColumn,
    StringColumn,
    intColumn
} from "$lib/components/datagrid/columns/types";

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
            base: intColumn,
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
