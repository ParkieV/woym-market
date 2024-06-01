import type { Column, ColumnGroup } from "$lib/components/datagrid/columns";
import {
    BooleanColumn,
    DateColumn,
    NumberColumn,
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
                    let diff = Math.max(0, params.data.min_stock - params.data.current_stock);
                    let { is_deliver_in_boxes, in_box } = params.data;
                    if (is_deliver_in_boxes) {
                        let boxes_remainder = 0;
                        if (diff % in_box !== 0) boxes_remainder = 1;
                        let boxes = Math.floor(diff / in_box) + boxes_remainder;
                        return boxes * in_box;
                    }
                    return diff;
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
