import type { Column, ColumnGroup } from "$lib/components/datagrid/columns";

export default function columnList(
    markets: { id: number; name: string }[]
): (Column | ColumnGroup)[] {
    return [
        { header: "SKU", key: "sku", data_type: "string", pinned: true },
        {
            header: "Информация",
            children: [
                { header: "Фото", key: "photo", data_type: "image" },
                { header: "Название", key: "name", data_type: "string" },
                {
                    header: "Примечание 1",
                    key: "note_1",
                    data_type: "string",
                    editable: true,
                    columnGroupShow: "closed"
                },
                {
                    header: "Примечание 2",
                    key: "note_2",
                    data_type: "string",
                    editable: true,
                    columnGroupShow: "closed"
                },
                {
                    header: "Примечание 3",
                    key: "note_3",
                    data_type: "string",
                    editable: true,
                    columnGroupShow: "closed"
                }
            ]
        },
        { header: "Мой склад", key: "own_storage", data_type: "int", editable: true },
        ...markets.map<Column>(x => ({
            header: `${x.name}, шт.`,
            key: `shops.${x.id}`,
            data_type: "int"
        })),
        { header: "Скрыт", key: "hidden", data_type: "boolean", editable: true }
    ];
}
