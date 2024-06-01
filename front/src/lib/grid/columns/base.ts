import type { Column, ColumnGroup } from "$lib/components/datagrid/columns";
import { GroupColumn, ImageColumn, StringColumn } from "$lib/components/datagrid/columns/types";

/** Columns that are used by few different grids. */
export default function baseOfferColumns(): (Column | ColumnGroup)[] {
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
                }
            ]
        }
    ];
}
